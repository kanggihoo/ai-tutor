"""① 결제 서비스: OrderCreated를 받아 결제 기록을 남긴다. 중복 방지 없음.

uv run m1_payment_service.py          # 새 메시지가 IDLE초 동안 없으면 종료
"""

import json

from common import PAYMENTS_DB, connect, consumer

IDLE = 5.0


def main() -> None:
    c = consumer("payment")
    with connect(PAYMENTS_DB) as conn:
        while True:
            msg = c.poll(IDLE)
            if msg is None:
                break
            if msg.error():
                raise SystemExit(msg.error())
            ev = json.loads(msg.value())
            with conn.transaction():
                conn.execute(
                    "INSERT INTO payments (order_id, amount) VALUES (%s, %s)",
                    (ev["order_id"], ev["amount"]),
                )
            print(f"paid {ev['order_id'][:8]} {ev['amount']}원 (offset {msg.offset()})")
    c.close()


if __name__ == "__main__":
    main()
