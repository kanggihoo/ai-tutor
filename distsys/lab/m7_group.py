"""⑦ 파티션 2개 + 같은 그룹의 소비자 A, B. A는 DB 커밋 직후 죽는다(CRASH_AT=after_db).
순서: topic 2파티션 → A, B 시작 → 각자 파티션 1개씩 받을 때까지 대기(sleep 없음)
      → P0·P1에 주문 1건씩 발행 → A 사망 → B가 P0까지 맡아 재수신(skip dup) → B 종료.
"""

import json
import os
import re
import subprocess
import sys
import threading
import time
import uuid

from confluent_kafka.admin import AdminClient, NewTopic

from common import BROKER, ORDERS_DB, TOPIC, connect, producer

lines: list[str] = []  # A, B 출력 전체(시간순). 두 reader 스레드가 같이 넣는다.


def start(name: str, env: dict) -> subprocess.Popen:
    p = subprocess.Popen([sys.executable, "m7_payment_service.py"], stdout=subprocess.PIPE,
                         text=True, env={**os.environ, "NAME": name, "PYTHONUNBUFFERED": "1", **env})

    def pump():
        for line in p.stdout:
            line = line.rstrip()
            lines.append(line)
            print(line, flush=True)
    threading.Thread(target=pump, daemon=True).start()
    return p


def wait_for(cond, what: str, timeout: float = 60) -> None:
    end = time.time() + timeout
    while not cond():
        if time.time() > end:
            raise SystemExit(f"timeout: {what}")
        time.sleep(0.1)


def last_assigned(name: str):
    found = [l for l in lines if l.startswith(f"[{name}] assigned")]
    return json.loads(re.search(r"\[.*\]", found[-1][len(f"[{name}]"):]).group()) if found else None


def main() -> None:
    admin = AdminClient({"bootstrap.servers": BROKER})
    admin.delete_topics([TOPIC])[TOPIC].result()
    for _ in range(20):  # 삭제가 끝나야 같은 이름으로 다시 만들 수 있다.
        try:
            admin.create_topics([NewTopic(TOPIC, num_partitions=2)])[TOPIC].result()
            break
        except Exception:
            time.sleep(0.5)

    a = start("A", {"CRASH_AT": "after_db"})
    b = start("B", {})
    # 각자 파티션 1개씩 받은 상태(리밸런스 끝)까지 기다린다.
    wait_for(lambda: len(last_assigned("A") or []) == 1 and len(last_assigned("B") or []) == 1,
             "A, B 파티션 분배")

    # P0, P1에 주문 1건씩. 주문 DB에 원본 행도 넣어 check.py가 누락/중복을 셀 수 있게 한다.
    p = producer()
    with connect(ORDERS_DB) as conn:
        for part in (0, 1):
            ev = {"event_id": str(uuid.uuid4()), "order_id": str(uuid.uuid4()),
                  "customer": "kim", "amount": 10000}
            conn.execute("INSERT INTO orders (id, customer, amount) VALUES (%s, 'kim', 10000)",
                         (ev["order_id"],))
            p.produce(TOPIC, key=ev["order_id"], value=json.dumps(ev), partition=part)
    p.flush(10)

    a.wait(timeout=30)  # A는 DB 커밋 직후 💥
    # B가 A의 파티션까지 맡아 같은 이벤트를 다시 받고 inbox가 막을 때까지.
    wait_for(lambda: any(l.startswith("[B] skip dup") for l in lines), "B의 재수신·skip")
    b.terminate()
    b.wait(timeout=10)


if __name__ == "__main__":
    main()
