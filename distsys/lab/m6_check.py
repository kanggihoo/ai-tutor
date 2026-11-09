"""⑥ 먼저 취소를 본 소비자가 뒤늦은 생성으로 결제하지 않았는지 확인한다."""

from common import ORDERS_DB, PAYMENTS_DB, connect


def inspect() -> dict:
    with connect(ORDERS_DB) as conn:
        orders = list(conn.execute("SELECT id, status FROM orders"))
    with connect(PAYMENTS_DB) as conn:
        states = list(conn.execute("SELECT order_id, version, status FROM payment_order_state"))
        paid = conn.execute("SELECT count(*) FROM payments").fetchone()[0]
    expected = [(order_id, 2, "cancelled") for order_id, _ in orders]
    errors = int(len(orders) != 1 or any(status != "cancelled" for _, status in orders))
    errors += int(states != expected)
    print(f"원본 주문 {[s for _, s in orders]}, 소비자 상태 {[(v, s) for _, v, s in states]}, 결제 {paid}건")
    return {"state_errors": errors, "payments": paid}
