"""② 주문과 outbox 저장. 트랜잭션 경계를 고치는 실습."""

import uuid

from psycopg.types.json import Jsonb

from common import ORDERS_DB, connect, crash_point


def main() -> None:
    event = {"event_id": str(uuid.uuid4()), "type": "OrderCreated",
             "order_id": str(uuid.uuid4()), "customer": "kim", "amount": 10000}
    # autocommit=True: 명시적 transaction 블록 밖의 SQL은 각각 커밋한다.
    with connect(ORDERS_DB) as conn:
        conn.autocommit = True
        # 주문과 발행할 이벤트를 함께 커밋한다. 중간에 죽으면 둘 다 롤백된다.
        with conn.transaction():
            conn.execute("INSERT INTO orders (id, customer, amount) VALUES (%s, %s, %s)",
                         (event["order_id"], event["customer"], event["amount"]))
            # 아직 커밋 전: 여기서 죽으면 위 주문 INSERT도 롤백된다.
            crash_point("between_inserts")
            conn.execute("INSERT INTO outbox (event_id, payload) VALUES (%s, %s)",
                         (event["event_id"], Jsonb(event)))
        # 두 저장이 끝났지만, 아직 브로커에 보내지는 않은 시점.
        crash_point("after_db")


if __name__ == "__main__":
    main()
