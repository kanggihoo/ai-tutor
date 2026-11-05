"""모든 미션이 같이 쓰는 연결 정보와 실험 훅."""

import os
import threading

import psycopg
import redis

DB = "postgresql://postgres:postgres@localhost:5433/shop"
TTL = 60  # 캐시 TTL(초). 옛 값이 박히면 최대 이만큼 남는다


def rds() -> redis.Redis:
    return redis.Redis(decode_responses=True)


def connect() -> psycopg.Connection:
    """`with connect() as conn:` 블록이 정상으로 끝나면 커밋, 예외면 롤백."""
    return psycopg.connect(DB)


# 이름 → (도착 신호, 재개 신호). run.py가 pause_at()으로 등록한다
_pauses: dict[str, tuple[threading.Event, threading.Event]] = {}


def pause_at(name: str) -> tuple[threading.Event, threading.Event]:
    """run.py 전용: name 지점에 처음 도착한 스레드를 재개 신호까지 멈춰 둔다."""
    _pauses[name] = (threading.Event(), threading.Event())
    return _pauses[name]


def hook(name: str) -> None:
    """실험용 지점. 평소엔 아무 일도 안 한다.

    - CRASH_AT=name 이면 프로세스를 즉시 죽인다(os._exit = kill -9, finally도 안 돈다).
    - run.py가 pause_at(name)을 걸어 두면 여기서 멈춘다(sleep 없이 순서를 고정).
    """
    if os.environ.get("CRASH_AT") == name:
        print(f"💥 CRASH at {name}", flush=True)
        os._exit(1)
    if name in _pauses:
        arrived, resume = _pauses.pop(name)  # 한 번만 멈춘다
        arrived.set()
        resume.wait()
