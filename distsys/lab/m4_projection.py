"""④ 주문 이벤트로 화면용 주문 목록·고객별 주문 합계를 만든다."""

import json
import os

from psycopg import sql

from common import PAYMENTS_DB, connect, consumer

# 조회 반영 이력은 결제 처리 이력과 별도로 기록한다.
INBOX_TABLE = "projection_processed_events"


def main() -> None:
    # 별도 그룹이므로 결제 그룹의 읽는 위치에 영향을 주지 않는다.
    c = consumer(os.environ.get("PROJECTION_GROUP", "projection"),
                 **{"enable.auto.commit": False})
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
                # 조회용 inbox와 두 조회 모델은 함께 커밋한다.
                with conn.transaction():
                    n = conn.execute(sql.SQL(
                        "INSERT INTO {} (event_id) VALUES (%s) "
                        "ON CONFLICT DO NOTHING"
                    ).format(sql.Identifier(INBOX_TABLE)), (ev["event_id"],)).rowcount
                    if n != 0:
                        # 주문별 목록은 order_id로 UPSERT한다.
                        conn.execute(
                            "INSERT INTO order_view (order_id, customer, amount) VALUES (%s, %s, %s) "
                            "ON CONFLICT (order_id) DO UPDATE SET "
                            "customer = EXCLUDED.customer, amount = EXCLUDED.amount",
                            (ev["order_id"], ev["customer"], ev["amount"]))
                        # 고객별 합계는 처음 처리한 이벤트에 대해서만 더한다.
                        conn.execute(
                            "INSERT INTO customer_totals (customer, total_amount) VALUES (%s, %s) "
                            "ON CONFLICT (customer) DO UPDATE SET total_amount = "
                            "customer_totals.total_amount + EXCLUDED.total_amount",
                            (ev["customer"], ev["amount"]))
                c.commit(message=msg, asynchronous=False)
                print(f"projection {'apply' if n else 'skip'} {ev['event_id'][:8]}")
    finally:
        c.close()


if __name__ == "__main__":
    main()
