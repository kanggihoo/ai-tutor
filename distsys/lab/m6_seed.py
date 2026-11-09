"""⑥ 같은 주문의 생성(v1)·취소(v2)를 업무 순서대로 outbox에 저장한다."""

import uuid

from psycopg.types.json import Jsonb

from common import ORDERS_DB, connect


def main() -> None:
    order_id = str(uuid.uuid4())
    with connect(ORDERS_DB) as conn:
        conn.execute("INSERT INTO orders (id, customer, amount) VALUES (%s, 'kim', 10000)",
                     (order_id,))
        ev = {"event_id": str(uuid.uuid4()), "type": "OrderCreated", "version": 1,
              "order_id": order_id, "customer": "kim", "amount": 10000}
        conn.execute("INSERT INTO outbox (event_id, payload) VALUES (%s, %s)",
                     (ev["event_id"], Jsonb(ev)))
    # 주문 생성이 커밋된 뒤 별도 트랜잭션으로 취소한다. 릴레이는 아직 실행 전이다.
    with connect(ORDERS_DB) as conn:
        conn.execute("UPDATE orders SET status = 'cancelled' WHERE id = %s", (order_id,))
        ev = {**ev, "event_id": str(uuid.uuid4()), "type": "OrderCancelled", "version": 2}
        conn.execute("INSERT INTO outbox (event_id, payload) VALUES (%s, %s)",
                     (ev["event_id"], Jsonb(ev)))
    print("원본 주문 cancelled, outbox: OrderCreated v1 → OrderCancelled v2")


if __name__ == "__main__":
    main()
