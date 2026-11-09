"""④ 조회 결과를 원본 주문과 대조한다. 결제 누락·중복은 기존 검사기가 확인한다."""

from common import ORDERS_DB, PAYMENTS_DB, connect


def inspect() -> int:
    with connect(ORDERS_DB) as conn:
        expected_rows = list(conn.execute(
            "SELECT id, customer, amount FROM orders ORDER BY id"))
        expected_totals = list(conn.execute(
            "SELECT customer, sum(amount) FROM orders GROUP BY customer ORDER BY customer"))
    with connect(PAYMENTS_DB) as conn:
        rows = list(conn.execute(
            "SELECT order_id, customer, amount FROM order_view ORDER BY order_id"))
        totals = list(conn.execute(
            "SELECT customer, total_amount FROM customer_totals ORDER BY customer"))
    print(f"조회 주문 {len(rows)}건, 고객별 주문 합계 {totals}")
    errors = int(rows != expected_rows) + int(totals != expected_totals)
    print(f"{'✅' if not errors else '❌'} 조회 모델: 원본 대조 불일치 {errors}개")
    return errors


if __name__ == "__main__":
    raise SystemExit(bool(inspect()))
