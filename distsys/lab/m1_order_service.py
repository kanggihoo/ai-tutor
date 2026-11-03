"""① 이중 쓰기: 주문 DB 저장과 Kafka 발행을 따로 한다.

uv run m1_order_service.py [주문 수]                          # 기본 db_first
ORDER_MODE=publish_first uv run m1_order_service.py 5
CRASH_AT=after_db@3 uv run m1_order_service.py 5              # 3번째 주문에서 저장 후 죽음
CRASH_AT=after_publish@3 ORDER_MODE=publish_first uv run m1_order_service.py 5
"""

import os
import random
import sys
import uuid

from common import ORDERS_DB, connect, crash_point, producer, publish


def save_order(conn, order: dict) -> None:
    # 주문 DB에 저장한다. 블록이 정상 종료되면 커밋, 예외가 나면 롤백된다.
    with conn.transaction():
        conn.execute(
            "INSERT INTO orders (id, customer, amount) VALUES (%s, %s, %s)",
            (order["order_id"], order["customer"], order["amount"]),
        )


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    mode = os.environ.get("ORDER_MODE", "db_first")
    p = producer()  # Kafka로 이벤트를 보내는 클라이언트
    with connect(ORDERS_DB) as conn:
        for i in range(1, n + 1):
            order = {
                "event_id": str(uuid.uuid4()),
                "type": "OrderCreated",
                "order_id": str(uuid.uuid4()),
                "customer": random.choice(["kim", "lee", "park"]),
                "amount": random.randrange(1000, 50000, 1000),
            }
            if mode == "db_first":
                # 1. 주문을 DB에 저장하고 커밋한다.
                save_order(conn, order)
                # 2. 실습용 장애 지점. CRASH_AT 설정이 맞으면 즉시 종료한다.
                #    설정이 없으면 그냥 통과한다. 이미 커밋한 주문은 남는다.
                crash_point("after_db")
                # 3. 주문 이벤트를 Kafka로 보내고 브로커의 성공 응답까지 기다린다.
                #    p: 발행 클라이언트, order_id: 메시지 키, order: 이벤트 내용
                publish(p, order["order_id"], order)
            else:
                # 비교 실험: Kafka 발행 → 장애 지점 → 주문 DB 저장 순서.
                publish(p, order["order_id"], order)
                crash_point("after_publish")
                save_order(conn, order)
            print(f"order {i}: {order['order_id'][:8]} {order['amount']}원")


if __name__ == "__main__":
    main()
