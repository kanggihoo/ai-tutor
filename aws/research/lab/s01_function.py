"""s01 (W0, W9) 함수 실행과 로그.

W0 같은 함수에 정상 / handler 예외 / timeout. 응답 StatusCode·FunctionError·payload를 구분한다.
   호출자 권한: lambda:InvokeFunction이 있는 learner / 없는 learner.
W9 CloudWatch Logs: print 표식과 REPORT 줄, 조회 주체의 logs:FilterLogEvents 유/무,
   실행 role의 log 전송 권한 유/무(AWS는 권한이 없으면 로그가 안 남는다).

AWS 기대값: https://docs.aws.amazon.com/lambda/latest/dg/python-exceptions.html
           https://docs.aws.amazon.com/lambda/latest/dg/monitoring-cloudwatchlogs.html
"""
from lib import Checker, allow, c, make_user, outcome, policy
from sl import DENIED, IAM, LOGS_ALLOW, function, find_logs, invoke, role, uid

ck = Checker("s01")
SRC = r'''
import time, uuid
INIT_ID = uuid.uuid4().hex[:8]
def handler(event, context):
    print("MARK-" + event.get("mark", "none") + " init=" + INIT_ID)
    m = event.get("mode", "ok")
    if m == "raise":
        raise ValueError("boom-" + event.get("mark", ""))
    if m == "sleep":
        time.sleep(event.get("s", 4))
    return {"ok": True, "initId": INIT_ID, "requestId": context.aws_request_id,
            "remainingMs": context.get_remaining_time_in_millis()}
'''
fn_arn = function("fn", SRC, role("fn-role", LOGS_ALLOW), timeout=2)
dev = make_user("dev", policy(allow("lambda:InvokeFunction", fn_arn),
                              allow("logs:FilterLogEvents", f"arn:aws:logs:us-east-1:000000000000:log-group:/aws/lambda/*")))
devstar = make_user("devstar", policy(allow("logs:FilterLogEvents", "*")))
nodev = make_user("nodev")
L = c("lambda", **dev)

# ---------- W0 ----------
m1 = uid()
r, body, ferr, _ = invoke(L, "fn", {"mark": m1})
ck.check("W0.ok.invoke", r, "ALLOW", body)
ck.check("W0.ok.FunctionError", ferr, None, body)
ck.check("W0.ok.remainingMs<=2000", isinstance(body, dict) and 0 < body.get("remainingMs", 0) <= 2000, True, body)
m2 = uid()
r, body, ferr, _ = invoke(L, "fn", {"mark": m2, "mode": "raise"})
ck.check("W0.raise.invoke(HTTP 200)", r, "ALLOW", body)
ck.check("W0.raise.FunctionError", ferr, "Unhandled", body)
ck.check("W0.raise.errorType", (body or {}).get("errorType") if isinstance(body, dict) else body, "ValueError", body)
m3 = uid()
r, body, ferr, dt = invoke(L, "fn", {"mark": m3, "mode": "sleep", "s": 5})
ck.check("W0.timeout.FunctionError", ferr, "Unhandled", body)
ck.check("W0.timeout.errorMessage has 'Task timed out'", "Task timed out" in str(body), True, body)
ck.info(f"timeout invoke wall={dt:.1f}s body={str(body)[:160]}")
r, d, _, _ = invoke(c("lambda", **nodev), "fn", {"mark": "x"})
ck.check("W0.caller-without-InvokeFunction", r, DENIED if IAM else "ALLOW", d)

# ---------- W9 ----------
G = "/aws/lambda/fn"
hits = find_logs(G, "MARK-" + m1)
ck.check("W9.print-line-in-/aws/lambda/fn", isinstance(hits, list) and len(hits) >= 1, True, hits)
rep = find_logs(G, "REPORT", timeout=15)
# 문서: START, END, REPORT가 log group에 들어간다. 실제: handler 출력만 들어간다(LoggingConfig 지정·JSON에서도 같음, 탐색 실행)
ck.check("W9.REPORT-line-present", isinstance(rep, list) and len(rep) >= 1, False, None, doc_diff=True,
         doc="lambda.md:1010 'write their logs, START, END and REPORT included, to the LogGroup'")
err = find_logs(G, "boom-" + m2)
ck.check("W9.exception-logged", isinstance(err, list) and len(err) >= 1, True, err)
to = find_logs(G, "Task timed out", timeout=15)
# AWS는 timeout을 함수 log stream에 남긴다. floci는 자기 컨테이너 로그에만 남긴다("Function fn timed out after 2s")
ck.check("W9.timeout-logged(AWS: yes)", isinstance(to, list) and len(to) >= 1, False, None, aws_diff=True)
r, d = outcome(c("logs", **dev).filter_log_events, logGroupName=G, filterPattern='"MARK-"')
# AWS: FilterLogEvents는 log-group ARN으로 인가. floci 로그: "action=logs:FilterLogEvents resource=*"
ck.check("W9.reader-with-FilterLogEvents(log-group scoped)", r, DENIED if IAM else "ALLOW", d, doc_diff=IAM,
         doc="iam.md:1820 CloudWatch Logs는 floci가 ARN을 직접 만든다 -> 실제 resource=*로 평가")
r, d = outcome(c("logs", **devstar).filter_log_events, logGroupName=G, filterPattern='"MARK-"')
ck.check("W9.reader-with-FilterLogEvents(Resource *)", r, "ALLOW", d)
r, d = outcome(c("logs", **nodev).filter_log_events, logGroupName=G, filterPattern='"MARK-"')
ck.check("W9.reader-without-FilterLogEvents", r, DENIED if IAM else "ALLOW", d)

# 실행 role에 logs 권한이 없을 때. AWS: 로그 그룹/스트림을 못 만들어 로그가 남지 않는다
function("fn-nolog", SRC, role("nolog-role"))
m4 = uid()
r, body, ferr, _ = invoke(c("lambda"), "fn-nolog", {"mark": m4})
ck.check("W9.nolog-role.invoke", r, "ALLOW", body)
hits = find_logs("/aws/lambda/fn-nolog", "MARK-" + m4, timeout=20)
ck.info(f"nolog-role log hits = {hits if not isinstance(hits, list) else len(hits)}")
ck.check("W9.nolog-role.log-delivered(AWS: no)", isinstance(hits, list) and len(hits) >= 1, True, hits, aws_diff=True,
         doc="lambda.md: 문서는 실행 role의 logs 권한을 언급하지 않음")

ck.done()
