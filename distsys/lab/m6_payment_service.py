"""⑥ 이벤트 중복뿐 아니라 업무 버전의 역전도 검사해야 하는 결제 소비자."""

import json

from common import PAYMENTS_DB, connect, consumer


def main() -> None:
    c = consumer("payment", **{"enable.auto.commit": False})
    try:
        with connect(PAYMENTS_DB) as conn:
            conn.autocommit = True
            while True:
                msg = c.poll(10)
                if msg is None:
                    break
                if msg.error():
                    raise RuntimeError(msg.error())
                ev = json.loads(msg.value())
                with conn.transaction():
                    n = conn.execute(
                        "INSERT INTO processed_events VALUES (%s) ON CONFLICT DO NOTHING",
                        (ev["event_id"],)).rowcount
                    conn.execute(
                        "INSERT INTO payment_order_state VALUES (%s, 0, 'unknown') ON CONFLICT DO NOTHING",
                        (ev["order_id"],))
                    latest = conn.execute(
                        "SELECT version FROM payment_order_state WHERE order_id = %s FOR UPDATE",
                        (ev["order_id"],)).fetchone()[0]
                    # 결정 지점: 처음 받은 event_id라면 무조건 적용해도 될까?
                    if n:
                        status = "cancelled"
                        if ev["type"] == "OrderCreated":
                            conn.execute("INSERT INTO payments (order_id, amount) VALUES (%s, %s)",
                                         (ev["order_id"], ev["amount"]))
                            status = "paid"
                        conn.execute(
                            "UPDATE payment_order_state SET version = %s, status = %s WHERE order_id = %s",
                            (ev["version"], status, ev["order_id"]))
                c.commit(message=msg, asynchronous=False)
                print(f"offset={msg.offset()} {ev['type']} v{ev['version']}, 처리 전 최신 version={latest}")
    finally:
        c.close()


if __name__ == "__main__":
    main()
