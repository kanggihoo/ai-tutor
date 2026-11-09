"""실험 전에 상태를 비운다: 두 DB의 테이블, 토픽, 컨슈머 그룹 오프셋.

uv run reset.py
"""

import time

from confluent_kafka import KafkaException
from confluent_kafka.admin import AdminClient, NewTopic

from common import BROKER, ORDERS_DB, PAYMENTS_DB, TOPIC, connect

ORDERS_SCHEMA = """
DROP TABLE IF EXISTS outbox;
CREATE TABLE outbox (
    event_id uuid PRIMARY KEY,
    payload jsonb NOT NULL,
    sent boolean NOT NULL DEFAULT false
);
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    id         uuid PRIMARY KEY,
    customer   text NOT NULL,
    amount     int  NOT NULL,
    status     text NOT NULL DEFAULT 'created',
    created_at timestamptz NOT NULL DEFAULT now()
);
DROP TABLE IF EXISTS order_processed_events;
CREATE TABLE order_processed_events (event_id uuid PRIMARY KEY);
"""

# order_id에 UNIQUE를 일부러 걸지 않는다: 중복 결제가 생기면 그대로 보여야 한다.
PAYMENTS_SCHEMA = """
DROP TABLE IF EXISTS payments;
CREATE TABLE payments (
    id         bigserial PRIMARY KEY,
    order_id   uuid NOT NULL,
    amount     int  NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
-- ③ inbox: 처리한 event_id 장부. PK 충돌 = 이미 처리한 이벤트.
DROP TABLE IF EXISTS processed_events;
CREATE TABLE processed_events (
    event_id uuid PRIMARY KEY
);
-- ④ 조회 모델은 결제 테이블과 별도로 관리한다(실습에서는 같은 DB에 둔다).
DROP TABLE IF EXISTS order_view;
CREATE TABLE order_view (
    order_id uuid PRIMARY KEY,
    customer text NOT NULL,
    amount int NOT NULL
);
DROP TABLE IF EXISTS customer_totals;
CREATE TABLE customer_totals (
    customer text PRIMARY KEY,
    total_amount bigint NOT NULL
);
DROP TABLE IF EXISTS projection_processed_events;
CREATE TABLE projection_processed_events (event_id uuid PRIMARY KEY);
-- ⑤ 결제 실패 기록과 실패 이벤트의 발행 버퍼.
DROP TABLE IF EXISTS payment_failures;
CREATE TABLE payment_failures (order_id uuid PRIMARY KEY, reason text NOT NULL);
DROP TABLE IF EXISTS payment_outbox;
CREATE TABLE payment_outbox (
    event_id uuid PRIMARY KEY,
    payload jsonb NOT NULL,
    sent boolean NOT NULL DEFAULT false
);
-- ⑥ 결제 소비자가 본 주문별 최신 업무 버전과 상태.
DROP TABLE IF EXISTS payment_order_state;
CREATE TABLE payment_order_state (
    order_id uuid PRIMARY KEY,
    version int NOT NULL,
    status text NOT NULL
);
"""

GROUPS = ["payment", "projection", "projection-replay", "orders-compensation"]


def main() -> None:
    for dsn, ddl in [(ORDERS_DB, ORDERS_SCHEMA), (PAYMENTS_DB, PAYMENTS_SCHEMA)]:
        with connect(dsn) as conn:
            conn.execute(ddl)

    admin = AdminClient({"bootstrap.servers": BROKER})
    for group in GROUPS:
        for _ in range(30):  # 죽은 컨슈머의 세션 만료까지 기다린다.
            try:
                admin.delete_consumer_groups([group])[group].result()
                break
            except KafkaException as e:
                if "NOT_EMPTY" not in str(e).upper() and "NON_EMPTY" not in str(e).upper():
                    break  # 없는 그룹은 무시한다.
                time.sleep(1)
    topics = admin.list_topics(timeout=10).topics
    for topic in [TOPIC, "payment-results"]:
        if topic in topics:
            admin.delete_topics([topic])[topic].result()
        for _ in range(20):  # 삭제가 끝나야 같은 이름으로 다시 만들 수 있다.
            try:
                admin.create_topics([NewTopic(topic, num_partitions=1)])[topic].result()
                break
            except KafkaException:
                time.sleep(0.5)
        else:
            raise SystemExit(f"topic 재생성 실패: {topic}")
    print("reset ok: orders/payments 테이블, 토픽, 컨슈머 그룹 비움")


if __name__ == "__main__":
    main()
