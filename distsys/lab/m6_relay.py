"""⑥ 릴레이 두 개의 SKIP LOCKED로 발행 순서 역전을 재현한다. sleep 없이 동기화한다."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event

from common import ORDERS_DB, connect, producer, publish


def main() -> None:
    locked = Event()
    cancelled_sent = Event()

    def worker(first: bool) -> None:
        if not first and not locked.wait(15):
            raise RuntimeError("워커 A의 행 잠금 대기 시간 초과")
        p = producer()
        with connect(ORDERS_DB) as conn:
            with conn.transaction():
                row = conn.execute(
                    "SELECT event_id, payload FROM outbox WHERE NOT sent "
                    "ORDER BY (payload->>'version')::int LIMIT 1 FOR UPDATE SKIP LOCKED"
                ).fetchone()
                if row is None:
                    raise RuntimeError("발행할 행 없음")
                event_id, ev = row
                if first:
                    print("워커 A: v1 행 잠금 획득, 발행 지연", flush=True)
                    locked.set()
                    if not cancelled_sent.wait(20):
                        raise RuntimeError("워커 B의 v2 발행 대기 시간 초과")
                # 두 워커 모두 같은 order_id key로 같은 partition에 발행한다.
                publish(p, ev["order_id"], ev)
                conn.execute("UPDATE outbox SET sent = true WHERE event_id = %s", (event_id,))
                print(f"워커 {'A' if first else 'B'}: {ev['type']} v{ev['version']} 발행 성공", flush=True)
                if not first:
                    cancelled_sent.set()

    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(worker, True)
        b = pool.submit(worker, False)
        a.result()
        b.result()


if __name__ == "__main__":
    main()
