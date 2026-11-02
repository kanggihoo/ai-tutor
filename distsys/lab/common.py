"""모든 미션이 같이 쓰는 연결 정보와 장애 주입 훅."""

import json
import os

import psycopg
from confluent_kafka import Consumer, Producer

BROKER = "localhost:19092"
TOPIC = "orders"
ORDERS_DB = "postgresql://postgres:postgres@localhost:5432/orders"
PAYMENTS_DB = "postgresql://postgres:postgres@localhost:5432/payments"

_hits: dict[str, int] = {}


def crash_point(name: str) -> None:
    """CRASH_AT=name 또는 name@N 이면 N번째(기본 1) 도달 때 프로세스를 즉시 죽인다.

    예외가 아니라 os._exit라서 except/finally/커밋이 하나도 실행되지 않는다 (= kill -9).
    """
    spec = os.environ.get("CRASH_AT", "")
    target, _, nth = spec.partition("@")
    if target != name:
        return
    _hits[name] = _hits.get(name, 0) + 1
    if _hits[name] == int(nth or 1):
        print(f"💥 CRASH at {name} (#{_hits[name]})", flush=True)
        os._exit(1)


def connect(dsn: str) -> psycopg.Connection:
    return psycopg.connect(dsn)


def producer() -> Producer:
    return Producer({"bootstrap.servers": BROKER})


def publish(p: Producer, key: str, event: dict) -> None:
    """발행하고 브로커 응답(delivery 결과)까지 기다린다. 실패하면 예외."""
    err: list = []
    p.produce(TOPIC, key=key, value=json.dumps(event),
              on_delivery=lambda e, _msg: err.append(e))
    p.flush(10)
    if not err or err[0] is not None:
        raise RuntimeError(f"publish failed: {err}")


def consumer(group: str, **overrides) -> Consumer:
    conf = {"bootstrap.servers": BROKER, "group.id": group,
            "auto.offset.reset": "earliest"}
    conf.update(overrides)
    c = Consumer(conf)
    c.subscribe([TOPIC])
    return c
