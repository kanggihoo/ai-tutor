"""⑦ 같은 그룹(payment)에 속한 결제 소비자 1명. NAME으로 A/B를 구분한다.
m3b와 같은 inbox + DB 커밋 뒤 오프셋 커밋. 다른 점: 파티션 할당 변화와 수신을 로그로 남긴다.

NAME=A uv run m7_payment_service.py
"""

import json
import os

from common import PAYMENTS_DB, connect, consumer, crash_point

NAME = os.environ["NAME"]
IDLE = 40.0  # driver가 먼저 종료시키므로 안전망일 뿐


def say(text: str) -> None:
    print(f"[{NAME}] {text}", flush=True)


def on_assign(c, parts):
    # broker가 이 소비자에게 맡긴 파티션. 리밸런스가 끝날 때마다 호출된다.
    say(f"assigned {sorted(p.partition for p in parts)}")
    c.assign(parts)


def on_revoke(c, parts):
    say(f"revoked {sorted(p.partition for p in parts)}")
    c.unassign()


def main() -> None:
    c = consumer("payment", **{"enable.auto.commit": False})
    c.subscribe(["orders"], on_assign=on_assign, on_revoke=on_revoke)
    with connect(PAYMENTS_DB) as conn:
        conn.autocommit = True
        while True:
            msg = c.poll(IDLE)
            if msg is None:
                break
            if msg.error():
                raise SystemExit(msg.error())
            ev = json.loads(msg.value())
            say(f"recv {ev['order_id'][:8]} P{msg.partition()} offset {msg.offset()}")

            with conn.transaction():
                n = conn.execute(
                    "INSERT INTO processed_events (event_id) VALUES (%s) "
                    "ON CONFLICT DO NOTHING", (ev["event_id"],)).rowcount
                if n != 0:
                    conn.execute(
                        "INSERT INTO payments (order_id, amount) VALUES (%s, %s)",
                        (ev["order_id"], ev["amount"]))
            # DB 커밋은 끝났고 오프셋 커밋은 아직: 여기서 죽으면 커밋 위치가 그대로 남는다.
            crash_point("after_db")
            c.commit(message=msg, asynchronous=False)
            say(("skip dup " if n == 0 else "paid ") + f"{ev['order_id'][:8]}, 오프셋 커밋")
    c.close()


if __name__ == "__main__":
    main()
