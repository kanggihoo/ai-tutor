"""불변식 검사: 주문마다 결제가 정확히 1건, 없는 주문의 결제(유령)는 0건.

uv run check.py
합계가 아니라 주문별로 센다 (유실 1건 + 중복 1건이 합계에서 상쇄되지 않게).
"""

import sys

from common import ORDERS_DB, PAYMENTS_DB, connect

LABELS = {"missing": "결제 누락", "dup": "중복 결제", "ghost": "유령 결제"}


def inspect() -> dict[str, list[str]]:
    with connect(ORDERS_DB) as conn:
        orders = {str(r[0]) for r in conn.execute("SELECT id FROM orders")}
    with connect(PAYMENTS_DB) as conn:
        paid = {str(r[0]): r[1] for r in conn.execute(
            "SELECT order_id, count(*) FROM payments GROUP BY order_id")}
    print(f"주문 {len(orders)}건, 결제된 주문 {len(paid)}건")
    return {
        "missing": sorted(o for o in orders if o not in paid),
        "dup": sorted(o for o in orders if paid.get(o, 0) > 1),
        "ghost": sorted(o for o in paid if o not in orders),
    }


def report(found: dict[str, list[str]]) -> dict[str, int]:
    for key, ids in found.items():
        mark = "✅" if not ids else "❌"
        print(f"{mark} {LABELS[key]}: {len(ids)}" + "".join(f"\n   - {i[:8]}" for i in ids))
    return {k: len(v) for k, v in found.items()}


if __name__ == "__main__":
    sys.exit(1 if any(report(inspect()).values()) else 0)
