"""실험 전에 상태를 비운다: 두 DB의 테이블, 토픽, 컨슈머 그룹 오프셋.

uv run reset.py
"""

import time

from confluent_kafka import KafkaException
from confluent_kafka.admin import AdminClient, NewTopic

from common import BROKER, ORDERS_DB, PAYMENTS_DB, TOPIC, connect

ORDERS_SCHEMA = """
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    id         uuid PRIMARY KEY,
    customer   text NOT NULL,
    amount     int  NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
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
"""

GROUPS = ["payment"]


def main() -> None:
    for dsn, ddl in [(ORDERS_DB, ORDERS_SCHEMA), (PAYMENTS_DB, PAYMENTS_SCHEMA)]:
        with connect(dsn) as conn:
            conn.execute(ddl)

    admin = AdminClient({"bootstrap.servers": BROKER})
    for f in admin.delete_consumer_groups(GROUPS).values():
        try:
            f.result()
        except KafkaException:
            pass  # 그룹이 아직 없으면 실패한다. 무시.
    if TOPIC in admin.list_topics(timeout=10).topics:
        admin.delete_topics([TOPIC])[TOPIC].result()
    for _ in range(20):  # 삭제가 끝나야 같은 이름으로 다시 만들 수 있다
        try:
            admin.create_topics([NewTopic(TOPIC, num_partitions=1)])[TOPIC].result()
            break
        except KafkaException:
            time.sleep(0.5)
    else:
        raise SystemExit("topic 재생성 실패")
    print("reset ok: orders/payments 테이블, 토픽, 컨슈머 그룹 비움")


if __name__ == "__main__":
    main()
