"""⑤ PaymentFailed를 받아 주문을 취소한다. 두 DB 작업의 경계가 결정 지점이다."""

import json

from common import ORDERS_DB, connect, consumer, crash_point


def main() -> None:
    c = consumer("orders-compensation", topic="payment-results",
                 **{"enable.auto.commit": False})
    try:
        with connect(ORDERS_DB) as conn:
            conn.autocommit = True
            while True:
                msg = c.poll(10)
                if msg is None:
                    break
                if msg.error():
                    raise RuntimeError(msg.error())
                ev = json.loads(msg.value())
                # inbox 기록과 주문 취소를 함께 커밋한다. 중간 장애 시 둘 다 롤백된다.
                with conn.transaction():
                    n = conn.execute(
                        "INSERT INTO order_processed_events VALUES (%s) ON CONFLICT DO NOTHING",
                        (ev["event_id"],)).rowcount
                    if n:
                        crash_point("before_cancel")
                        # 기존 주문 생성과는 별개인 이번 트랜잭션에서 취소 상태를 저장한다.
                        conn.execute("UPDATE orders SET status = 'cancelled' WHERE id = %s",
                                     (ev["order_id"],))
                c.commit(message=msg, asynchronous=False)
                print(f"cancel {'apply' if n else 'skip'} {ev['order_id'][:8]}")
    finally:
        c.close()


if __name__ == "__main__":
    main()
