"""⑤ 결제 실패 주문이 취소됐는지 확인한다. 결제 미발생은 이 미션의 정상 결과다."""

from common import ORDERS_DB, PAYMENTS_DB, connect


def inspect() -> dict:
    with connect(ORDERS_DB) as conn:
        orders = {str(r[0]): r[1] for r in conn.execute("SELECT id, status FROM orders")}
    with connect(PAYMENTS_DB) as conn:
        failures = {str(r[0]) for r in conn.execute("SELECT order_id FROM payment_failures")}
        paid = conn.execute("SELECT count(*) FROM payments").fetchone()[0]
        outbox = conn.execute("SELECT count(*), count(*) FILTER (WHERE sent) FROM payment_outbox").fetchone()
    errors = sum(orders.get(order_id) != "cancelled" for order_id in failures)
    errors += len(set(orders) ^ failures)
    errors += int(outbox != (len(failures), len(failures)))
    print(f"주문 상태 {list(orders.values())}, 결제 실패 {len(failures)}건, 실제 결제 {paid}건")
    print(f"{'✅' if not errors else '❌'} 보상 불일치 {errors}개")
    return {"compensation_errors": errors, "payments": paid}
