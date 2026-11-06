"""기존 run.py를 수정하지 않고 같은 시나리오를 개선 버전에 적용한다.

uv run run_versioned.py 1a-race
uv run run_versioned.py all
각 시나리오는 실습 DB와 Redis를 초기화한다(기존 run.py와 동일).
"""

import os
import subprocess
import sys

import m1a_versioned as versioned
import run as scenarios


def crash_run(cmd: str, crash_at: str) -> None:
    subprocess.run(
        [sys.executable, "m1a_versioned.py", *cmd.split()],
        env={**os.environ, "CRASH_AT": crash_at, "PYTHONIOENCODING": "utf-8"},
        check=False,  # commit 직후 사망하는 것이 실험의 의도다.
    )


def boundaries() -> None:
    r = versioned.r
    k = versioned.key(1)
    versioned.update(1, 200)
    assert r.hget(k, "tomb") == "1"
    assert r.eval(versioned.FILL, 1, k, 100, 1, 60) == 0
    assert versioned.read(1)["cache_stored"] is True
    assert versioned.read(1)["from"] == "cache"
    # 더 오래된 변경 이벤트와 채우기가 최신 버전을 덮지 못한다.
    versioned.update(1, 300)
    assert r.eval(versioned.INVALIDATE, 1, k, 2, 60) == 0
    assert r.hget(k, "v") == "3"
    # 만료 직후 상태를 기다림 없이 만든다. 기준이 사라지면 v1도 허용된다.
    r.pexpire(k, 0)
    assert r.eval(versioned.FILL, 1, k, 100, 1, 60) == 1
    print("   묘비 거절·조회 채우기·역순 무효화 확인. 만료 후 v1 저장 허용도 확인.")


if __name__ == "__main__":
    # 같은 reset·경쟁 순서·검사기를 재사용하되 구현과 사망 대상만 교체한다.
    scenarios.m1a = versioned
    scenarios.crash_run = crash_run
    scenarios.SCENARIOS["1a-boundaries"] = (
        "묘비 보호 범위와 만료 한계",
        boundaries,
        {"stale": 1},
    )
    sys.exit(scenarios.main())
