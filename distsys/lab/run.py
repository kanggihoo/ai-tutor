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
    "6-reordered": ("⑥ v2 취소를 먼저 받고 v1 생성은 나중에 받음", [
        ("m6_seed.py", {}),
        ("m6_relay.py", {}),
        ("m6_payment_service.py", {}),
    ], {"state_errors": 0, "payments": 0}),
    "5-cancel-crash": ("⑤ 실패 이벤트 기록 후 주문 취소 전 장애", [
        ("m2_order_service.py", {}),
        ("m2_relay.py", {}),
        ("m5_payment_service.py", {}),
        ("m5_relay.py", {}),
        ("m5_order_consumer.py", {"CRASH_AT": "before_cancel"}),
        ("m5_order_consumer.py", {}),
    ], {"compensation_errors": 0, "payments": 0}),
    "5-failure-dup": ("⑤ 실패 이벤트를 중복 발행해도 주문 취소", [
        ("m2_order_service.py", {}),
        ("m2_relay.py", {}),
        ("m5_payment_service.py", {"CRASH_AT": "after_failure_db"}),
        ("m5_payment_service.py", {}),
        ("m5_relay.py", {"CRASH_AT": "after_failure_publish"}),
        ("m5_relay.py", {}),
        ("m5_order_consumer.py", {}),
    ], {"compensation_errors": 0, "payments": 0}),
    "4-projection-dup": ("④ 중복 주문 이벤트: 목록 1건·합계 10000원이어야 함", [
        ("m2_order_service.py", {}),
        ("m2_relay.py", {"CRASH_AT": "after_publish"}),
        ("m2_relay.py", {}),
        ("m3b_payment_service.py", {}),
        ("m4_projection.py", {}),
    ], {**OK, "projection_errors": 0}),
    "4-replay": ("④ 조회 모델만 비우고 새 그룹으로 재생: 결제는 그대로", [
        ("m2_order_service.py", {}),
        ("m2_order_service.py", {}),
        ("m2_relay.py", {}),
        ("m3b_payment_service.py", {}),
        ("m4_projection.py", {}),
        ("m4_rebuild.py", {}),
    ], {**OK, "projection_errors": 0}),
    "2-atomic": ("② 두 INSERT 사이 장애: 원자성 확인", [
        ("m2_order_service.py", {"CRASH_AT": "between_inserts"}),
        ("m2_relay.py", {}),
        ("m1_payment_service.py", {}),
    ], OK),
    "2-after-db": ("② DB 저장 후 죽어도 릴레이가 발행", [
        ("m2_order_service.py", {"CRASH_AT": "after_db"}),
        ("m2_relay.py", {}),
        ("m1_payment_service.py", {}),
    ], OK),
    "2-duplicate": ("② 발행 후 표시 전 장애: 재발행 관찰", [
        ("m2_order_service.py", {}),
        ("m2_relay.py", {"CRASH_AT": "after_publish"}),
        ("m2_relay.py", {}),
        ("m1_payment_service.py", {}),
    ], {**OK, "dup": 1}),
    "3-inbox-crash": ("③ inbox 기록 후 결제 전 장애: 재전달돼도 결제 1건", [
        ("m2_order_service.py", {}),
        ("m2_relay.py", {}),
        ("m3_payment_service.py", {"CRASH_AT": "after_inbox"}),
        ("m3_payment_service.py", {}),
    ], OK),
    "3-inbox-dup": ("③ outbox 중복 발행도 inbox가 막는다", [
        ("m2_order_service.py", {}),
        ("m2_relay.py", {"CRASH_AT": "after_publish"}),
        ("m2_relay.py", {}),
        ("m3_payment_service.py", {}),
    ], OK),
    "3-offset-auto": ("③-b 처리가 6초 걸리다 죽음: 자동 오프셋 커밋이 먼저 나가면 누락", [
        ("m2_order_service.py", {}),
        ("m2_relay.py", {}),
        ("m3b_payment_service.py", {"CRASH_AT": "after_inbox", "SLOW": "6"}),
        ("m3b_payment_service.py", {}),
    ], OK),
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
    if name.startswith("6-"):
        from m6_check import inspect as inspect_ordering
        got = inspect_ordering()
    elif name.startswith("5-"):
        from m5_check import inspect as inspect_compensation
        got = inspect_compensation()
    else:
        got = check.report(check.inspect())
    if name.startswith("4-"):
        from m4_check import inspect
        got["projection_errors"] = inspect()
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
