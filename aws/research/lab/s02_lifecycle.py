"""s02 (W10, W11, W12) 실행 환경 수명과 cold start. LAB_IDLE(초)로 floci의 idle 회수 시간을 짧게 둔다.

W10a 연속 호출 3번: 같은 initId, count 1→2→3 (warm 재사용)
W10b 겹친 호출 3개(warm 1개가 이미 있음): 서로 다른 initId 3개, 새 init은 2개 이상
W10c idle 회수: 아무 호출 없이 LAB_IDLE*2+30초 기다린 뒤 호출 → 새 initId
W10d 무거운 init(INIT_SLEEP=2초): 첫 호출만 느리고 warm 호출은 빠름 (상대 비교만, 수치는 AWS 값 아님)
W11 provisioned concurrency 1 (published version + alias): READY 뒤 첫 호출은 initType=provisioned-concurrency, count=1
    (handler는 provisioning 때 안 돎), init은 호출 전에 끝나 있음. 한 호출을 잡아 둔 채 두 번째 → on-demand spillover
W12 로그로 init/호출 구분: REPORT `Init Duration`은 floci가 내지 않으므로(s01) handler가 찍은 init 로그로만 관찰

AWS 기대값: https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html
           https://docs.aws.amazon.com/lambda/latest/dg/provisioned-concurrency.html
"""
import os
import threading
import time

from lib import Checker, outcome
from sl import LOGS_ALLOW, function, find_logs, invoke, lam, role

ck = Checker("s02")
IDLE = int(os.environ.get("LAB_IDLE", "300"))
SRC = r'''
import os, time, uuid
INIT_AT = time.time()
time.sleep(float(os.environ.get("INIT_SLEEP", "0")))
INIT_ID = uuid.uuid4().hex[:8]
INIT_TYPE = os.environ.get("AWS_LAMBDA_INITIALIZATION_TYPE", "")
print("INIT " + INIT_ID + " type=" + INIT_TYPE)
COUNT = 0
def handler(event, context):
    global COUNT
    COUNT += 1
    print("INVOKE " + INIT_ID + " count=" + str(COUNT))
    if event.get("s"):
        time.sleep(event["s"])
    return {"initId": INIT_ID, "count": COUNT, "initType": INIT_TYPE, "initAt": INIT_AT, "now": time.time()}
'''
R = role("life-role", LOGS_ALLOW)

# ---------- W10a ----------
function("life", SRC, R)
seq = [invoke(lam, "life", {})[1] for _ in range(3)]
ck.check("W10a.sequential.same-initId", len({b["initId"] for b in seq}), 1, seq)
ck.check("W10a.sequential.count", ",".join(str(b["count"]) for b in seq), "1,2,3", seq)
warm_id = seq[0]["initId"]

# ---------- W10b ----------
res = []


def one(s=4, name="life", **kw):
    res.append(invoke(lam, name, {"s": s}, **kw)[1])


ts = [threading.Thread(target=one) for _ in range(3)]
[t.start() for t in ts]
[t.join() for t in ts]
ids = {b["initId"] for b in res if isinstance(b, dict)}
new_inits = len(ids - {warm_id})
ck.info(f"burst initIds={sorted(ids)} warm={warm_id} new={new_inits}")
ck.check("W10b.burst3.distinct-initIds", len(ids), 3, res)
ck.check("W10b.burst3.new-inits>=2", new_inits >= 2, True, res)

# ---------- W10c ----------
wait = IDLE * 2 + 30
ck.info(f"idle wait {wait}s (LAB_IDLE={IDLE})")
time.sleep(wait)
b = invoke(lam, "life", {})[1]
ck.check("W10c.after-idle.new-initId", b["initId"] not in ids | {warm_id}, True, b)
ck.check("W10c.after-idle.count", b["count"], 1, b)

# ---------- W10d ----------
function("heavy", SRC, R, env={"INIT_SLEEP": "2"})
_, b1, _, t1 = invoke(lam, "heavy", {})
_, b2, _, t2 = invoke(lam, "heavy", {})
ck.info(f"heavy init: cold wall={t1:.2f}s warm wall={t2:.2f}s (floci Docker 수치, AWS 값 아님)")
ck.check("W10d.cold-slower-than-warm-by>=1.5s", t1 - t2 >= 1.5, True, [t1, t2])
ck.check("W10d.same-env", b1["initId"] == b2["initId"], True, [b1, b2])

# ---------- W11 ----------
function("pc", SRC, R, env={"INIT_SLEEP": "2"})
ver = lam.publish_version(FunctionName="pc")["Version"]
lam.create_alias(FunctionName="pc", Name="live", FunctionVersion=ver)
r, d = outcome(lam.put_provisioned_concurrency_config, FunctionName="pc", Qualifier="live",
               ProvisionedConcurrentExecutions=1)
ck.check("W11.put-provisioned", r, "ALLOW", d)
st = None
for _ in range(90):
    st = lam.get_provisioned_concurrency_config(FunctionName="pc", Qualifier="live").get("Status")
    if st in ("READY", "FAILED"):
        break
    time.sleep(2)
ck.check("W11.status", st, "READY")
time.sleep(3)
_, b, _, t = invoke(lam, "pc", {}, Qualifier="live")
ck.info(f"PC first invoke wall={t:.2f}s body={b}")
ck.check("W11.first.initType", b.get("initType"), "provisioned-concurrency", b)
ck.check("W11.first.count(handler not run during provisioning)", b.get("count"), 1, b)
ck.check("W11.first.init-done-before-invoke(>=2s earlier)", b["now"] - b["initAt"] >= 3, True, b)
ck.check("W11.first.no-cold-wait(<1.5s, INIT_SLEEP=2)", t < 1.5, True, t)
pc_id = b["initId"]
res = []
th = threading.Thread(target=one, kwargs={"s": 5, "name": "pc", "Qualifier": "live"})
th.start()
time.sleep(1.5)
_, b2, _, t2 = invoke(lam, "pc", {}, Qualifier="live")
th.join()
ck.info(f"spillover: held={res} second={b2} wall={t2:.2f}s")
# AWS는 on-demand 환경에 AWS_LAMBDA_INITIALIZATION_TYPE=on-demand를 준다. floci는 provisioned에만 값을 준다(빈 문자열)
ck.check("W11.spillover.second-initType(AWS: on-demand)", b2.get("initType"), "", b2, aws_diff=True,
         doc="lambda.md Provisioned concurrency: provisioned runtimes receive AWS_LAMBDA_INITIALIZATION_TYPE=provisioned-concurrency (on-demand 언급 없음)")
ck.check("W11.spillover.second-new-env", b2.get("initId") != pc_id, True, b2)
ck.check("W11.spillover.second-paid-cold-start(>=1.5s)", t2 >= 1.5, True, t2)
r, d, _, _ = invoke(lam, "pc", {})  # $LATEST: PC 대상 아님
ck.check("W11.$LATEST-not-provisioned(initType empty)", d.get("initType") if isinstance(d, dict) else d, "", d, aws_diff=True)

# ---------- W12 ----------
hits = find_logs("/aws/lambda/life", "INIT ", timeout=20)
n_init = len(hits) if isinstance(hits, list) else -1
ck.info(f"INIT lines in /aws/lambda/life = {n_init}")
ck.check("W12.init-lines-match-distinct-envs(>=4)", n_init >= 4, True, hits)

ck.done()
