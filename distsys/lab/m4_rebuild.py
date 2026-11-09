"""④ 조회 모델만 비우고 새 그룹으로 Kafka 처음부터 재구축한다."""

import os

from common import PAYMENTS_DB, connect
from m4_projection import main as project


def main() -> None:
    # 주문·결제·결제 inbox·Kafka topic은 그대로 둔다.
    with connect(PAYMENTS_DB) as conn:
        conn.execute("TRUNCATE order_view, customer_totals, projection_processed_events")
    # reset 후 이 시나리오에서 아직 쓰지 않은 그룹. earliest부터 읽는다.
    os.environ["PROJECTION_GROUP"] = "projection-replay"
    project()


if __name__ == "__main__":
    main()
