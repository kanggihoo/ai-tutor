"""⑤ payments DB의 실패 이벤트를 payment-results topic으로 전달한다."""

from common import PAYMENTS_DB, connect, crash_point, producer, publish


def main() -> None:
    p = producer()
    with connect(PAYMENTS_DB) as conn:
        while True:
            with conn.transaction():
                row = conn.execute(
                    "SELECT event_id, payload FROM payment_outbox WHERE NOT sent "
                    "ORDER BY event_id LIMIT 1 FOR UPDATE SKIP LOCKED").fetchone()
                if row is None:
                    break
                event_id, ev = row
                publish(p, ev["order_id"], ev, topic="payment-results")
                crash_point("after_failure_publish")
                conn.execute("UPDATE payment_outbox SET sent = true WHERE event_id = %s", (event_id,))
                print(f"sent PaymentFailed {event_id}")


if __name__ == "__main__":
    main()
