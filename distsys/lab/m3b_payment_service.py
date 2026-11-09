"""③-b 결제 서비스 + inbox + 오프셋 경계. 오프셋 커밋 시점을 고치는 실습.
DB 처리 완료 후 Kafka 오프셋을 직접 커밋한다.

uv run m3b_payment_service.py     # 새 메시지가 IDLE초 동안 없으면 종료
"""

import json

import os
import time

from common import PAYMENTS_DB, connect, consumer, crash_point

IDLE = 10.0  # 죽은 컨슈머 뒤 그룹 재가입 대기 포함


def main() -> None:
    # DB 처리 전에 Kafka 소비 위치가 자동 저장되지 않도록 한다.
    c = consumer("payment", **{"enable.auto.commit": False})
    with connect(PAYMENTS_DB) as conn:
        # autocommit=True: 명시적 transaction 블록 밖의 SQL은 각각 바로 커밋한다.
        conn.autocommit = True
        while True:
            msg = c.poll(IDLE)  # Kafka(topic orders)에서 메시지 1개 수신
            if msg is None:
                break
            if msg.error():
                raise SystemExit(msg.error())
            ev = json.loads(msg.value())

            # ㉠㉡을 한 트랜잭션으로 묶는다. 중간에 죽으면 둘 다 롤백된다.
            with conn.transaction():
                # ㉠ payments DB의 processed_events에 이 event_id를 기록한다.
                #    PK 충돌이면 0행: 이미 처리한 이벤트.
                n = conn.execute(
                    "INSERT INTO processed_events (event_id) VALUES (%s) "
                    "ON CONFLICT DO NOTHING", (ev["event_id"],)).rowcount
                if n != 0:
                    # SLOW초 동안 처리가 느린 상황을 흉내 낸다 (예: DB가 느림).
                    time.sleep(float(os.environ.get("SLOW", "0")))
                    crash_point("after_inbox")  # ㉠ 후, ㉡ 전: 아직 커밋 전

                    # ㉡ payments DB의 payments에 결제를 기록한다.
                    conn.execute(
                        "INSERT INTO payments (order_id, amount) VALUES (%s, %s)",
                        (ev["order_id"], ev["amount"]))
            # DB 커밋 완료 뒤 Kafka에 다음 위치 저장. 이미 처리한 중복도 포함한다.
            c.commit(message=msg, asynchronous=False)
            if n == 0:
                print(f"skip dup {ev['event_id'][:8]}")
                continue
            print(f"paid {ev['order_id'][:8]} {ev['amount']}원 (offset {msg.offset()})")
    c.close()


if __name__ == "__main__":
    main()
