"""⑤ 가짜 결제 실패를 기록하고 PaymentFailed를 outbox에 함께 저장한다."""

import json
import uuid

from psycopg.types.json import Jsonb

from common import PAYMENTS_DB, connect, consumer, crash_point


def main() -> None:
    c = consumer("payment", **{"enable.auto.commit": False})
    try:
        with connect(PAYMENTS_DB) as conn:
            conn.autocommit = True
            while True:
                msg = c.poll(10)
                if msg is None:
                    break
                if msg.error():
                    raise RuntimeError(msg.error())
                ev = json.loads(msg.value())
                with conn.transaction():
                    n = conn.execute(
                        "INSERT INTO processed_events VALUES (%s) ON CONFLICT DO NOTHING",
                        (ev["event_id"],)).rowcount
                    if n:
                        # 이번 시나리오에서는 실제 PG 없이 항상 잔액 부족으로 실패시킨다.
                        conn.execute("INSERT INTO payment_failures VALUES (%s, %s)",
                                     (ev["order_id"], "insufficient_funds"))
                        failed = {"event_id": str(uuid.uuid4()), "type": "PaymentFailed",
                                  "order_id": ev["order_id"], "reason": "insufficient_funds"}
                        conn.execute("INSERT INTO payment_outbox (event_id, payload) VALUES (%s, %s)",
                                     (failed["event_id"], Jsonb(failed)))
                crash_point("after_failure_db")  # DB에는 실패와 발행할 이벤트가 모두 남는다.
                c.commit(message=msg, asynchronous=False)
                print(f"payment failed {ev['order_id'][:8]}")
    finally:
        c.close()


if __name__ == "__main__":
    main()
