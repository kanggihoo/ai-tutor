"""시나리오 하나를 처음부터 재현한다: reset → 단계 실행 → check → 기대값 비교.

uv run run.py                 # 시나리오 목록
uv run run.py 1-db-first      # 하나 실행
uv run run.py all             # 전부 실행 (회귀 테스트). 하나라도 기대와 다르면 exit 1

기대값(expect)은 "미션을 끝낸 뒤 나와야 하는 결과"다.
관찰 시나리오(①)는 깨진 결과가 기대값이고, 고치기 시나리오는 고치기 전엔 ❌가 정상이다.
"""

import os
import subprocess
import sys

import check
import reset

OK = {"missing": 0, "dup": 0, "ghost": 0}

# 이름: (설명, [(스크립트와 인자, 환경변수)], 기대값)
SCENARIOS = {
    "1-ok": ("① 장애 없음", [
        ("m1_order_service.py 3", {}),
        ("m1_payment_service.py", {}),
    ], OK),
    "1-db-first": ("① DB 저장 후 발행 전에 죽음", [
        ("m1_order_service.py 5", {"CRASH_AT": "after_db@3"}),
        ("m1_payment_service.py", {}),
    ], {**OK, "missing": 1}),
    "1-publish-first": ("① 발행 후 DB 저장 전에 죽음", [
        ("m1_order_service.py 5", {"CRASH_AT": "after_publish@3", "ORDER_MODE": "publish_first"}),
        ("m1_payment_service.py", {}),
    ], {**OK, "ghost": 1}),
}


def run(name: str) -> bool:
    desc, steps, expect = SCENARIOS[name]
    print(f"\n=== {name}: {desc}")
    reset.main()
    for cmd, env in steps:
        script, *args = cmd.split()
        shown = " ".join(f"{k}={v}" for k, v in env.items())
        print(f"$ {shown} {cmd}".replace("$  ", "$ "))
        # 장애 주입 단계는 exit 1로 끝나는 게 정상이라 종료 코드는 보지 않는다
        subprocess.run([sys.executable, script, *args], env={**os.environ, "PYTHONUNBUFFERED": "1", **env})
    got = check.report(check.inspect())
    ok = got == expect
    print("🎯 기대와 일치" if ok else f"⚠️ 기대와 다름: 기대 {expect}, 실제 {got}")
    return ok


def main() -> int:
    sys.stdout.reconfigure(line_buffering=True)  # 자식 출력과 순서가 섞이지 않게
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "all":
        results = {n: run(n) for n in SCENARIOS}
        print("\n" + "\n".join(f"{'✅' if ok else '❌'} {n}" for n, ok in results.items()))
        return 0 if all(results.values()) else 1
    if arg in SCENARIOS:
        return 0 if run(arg) else 1
    for n, (desc, _, _) in SCENARIOS.items():
        print(f"{n:20} {desc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
