"""시나리오 하나를 처음부터 재현한다: reset → 단계 실행 → check → 기대값 비교.

uv run run.py              # 시나리오 목록
uv run run.py 1a-race      # 하나 실행
uv run run.py all          # 전부 (회귀). 하나라도 기대와 다르면 exit 1
uv run run.py check        # 지금 상태만 검사

기대값은 "미션을 끝낸 뒤 나와야 하는 결과"다. 고치기 시나리오는 고치기 전엔 ⚠️가 정상.
"""

import os
import subprocess
import sys
import threading

import m1a_cache as m1a
from common import connect, pause_at, rds

r = rds()


def reset() -> None:
    """DB 상품 1개(id=1, 가격 100, 버전 1)로 되돌리고 Redis를 비운다."""
    with connect() as conn:
        conn.execute("DROP TABLE IF EXISTS products")
        conn.execute(
            "CREATE TABLE products (id int PRIMARY KEY, price int NOT NULL,"
            " version int NOT NULL)"
        )
        conn.execute("INSERT INTO products VALUES (1, 100, 1)")
    r.flushdb()


def check() -> dict:
    """캐시가 DB와 다른 버전을 들고 있으면 stale=1."""
    with connect() as conn:
        price, v = conn.execute(
            "SELECT price, version FROM products WHERE id = 1"
        ).fetchone()
    cached = r.hgetall(m1a.key(1))
    ttl = r.ttl(m1a.key(1))
    print(f"   DB: price={price} v={v} | 캐시: {cached or '(없음)'} ttl={ttl}")
    stale = int(bool(cached) and int(cached.get("v", 0)) != v and "tomb" not in cached)
    return {"stale": stale}


def crash_run(cmd: str, crash_at: str) -> None:
    """별도 프로세스로 실행하고 crash_at 지점에서 죽인다(진짜 프로세스 사망)."""
    print(f"$ CRASH_AT={crash_at} m1a_cache.py {cmd}")
    subprocess.run(
        [sys.executable, "m1a_cache.py", *cmd.split()],
        env={**os.environ, "CRASH_AT": crash_at, "PYTHONUNBUFFERED": "1"},
        check=False,  # 죽는 게 정상이라 종료 코드는 안 본다
    )


# ── 시나리오 단계 ──────────────────────────────────────────────


def race() -> None:
    """읽기 A가 DB에서 v1을 읽고 멈춘 사이, 쓰기 B가 v2로 바꾸고 캐시를 지운다. 그다음 A가 재개."""
    arrived, resume = pause_at("after_db_read")
    a = threading.Thread(target=lambda: print("   A:", m1a.read(1)))
    a.start()
    arrived.wait()
    print("   A: DB에서 읽고 멈춤 → B: update(1, 200)")
    m1a.update(1, 200)
    resume.set()
    a.join()


def crash_after_commit() -> None:
    print("   A:", m1a.read(1))  # 캐시를 v1로 채워 둔다
    crash_run("update 1 200", "after_commit")


def normal() -> None:
    print("   A:", m1a.read(1))
    m1a.update(1, 200)
    print("   B: update(1, 200)")
    print("   C:", m1a.read(1))


# 이름: (설명, 단계, 기대값)
SCENARIOS = {
    "1a-ok": ("①-a 경쟁 없음: 읽기 → 갱신 → 읽기", normal, {"stale": 0}),
    "1a-race": ("①-a 늦은 읽기가 옛 값을 재삽입", race, {"stale": 0}),
    "1a-crash": (
        "①-a 커밋 후 무효화 전에 죽음 (관찰)",
        crash_after_commit,
        {"stale": 1},
    ),
}


def run(name: str) -> bool:
    desc, step, expect = SCENARIOS[name]
    print(f"\n=== {name}: {desc}")
    reset()
    step()
    got = check()
    ok = got == expect
    print("🎯 기대와 일치" if ok else f"⚠️ 기대와 다름: 기대 {expect}, 실제 {got}")
    return ok


def main() -> int:
    sys.stdout.reconfigure(line_buffering=True)  # 자식 프로세스 출력과 순서가 안 섞이게
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "all":
        results = {n: run(n) for n in SCENARIOS}
        print(
            "\n" + "\n".join(f"{'✅' if ok else '❌'} {n}" for n, ok in results.items())
        )
        return 0 if all(results.values()) else 1
    if arg == "check":
        print(check())
        return 0
    if arg in SCENARIOS:
        return 0 if run(arg) else 1
    for n, (desc, _, _) in SCENARIOS.items():
        print(f"{n:12} {desc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
