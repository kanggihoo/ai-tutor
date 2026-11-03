"""② 폴링 릴레이. 실습에서는 대기 없이 현재 미발행 행을 모두 보내고 종료한다."""

from common import ORDERS_DB, connect, crash_point, producer, publish


def main() -> None:
    p = producer()
    with connect(ORDERS_DB) as conn:
        while True:
            with conn.transaction():
                # 다른 워커가 잡은 행은 건너뛴다. 잠금은 트랜잭션 종료까지 유지.
                row = conn.execute(
                    "SELECT event_id, payload FROM outbox WHERE NOT sent "
                    "ORDER BY event_id LIMIT 1 FOR UPDATE SKIP LOCKED").fetchone()
                if row is None:
                    break
                event_id, event = row
                # 저장된 event_id를 그대로 재사용해 Redpanda에 전송한다.
                publish(p, event["order_id"], event)
                crash_point("after_publish")
                # 브로커 성공 응답을 받은 뒤에만 발행 완료로 표시한다.
                conn.execute("UPDATE outbox SET sent = true WHERE event_id = %s", (event_id,))
                print(f"sent {event_id}")


if __name__ == "__main__":
    main()
