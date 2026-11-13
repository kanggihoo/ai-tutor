"""서버리스 검증(s01~s05) 공통 도구.

- bootstrap(자원 생성)은 `test` key로, 판정 대상 요청은 IAM user(learner)나 Lambda 실행 role로 한다.
- 함수 코드는 문자열로 받아 zip으로 올린다. runtime python3.12 (boto3 포함 이미지).
"""
import io
import json
import os
import time
import uuid
import zipfile

from lib import c, outcome, policy, allow, deny, wait_until

IAM = os.environ.get("LAB_IAM") == "true"
SIG = os.environ.get("LAB_SIG") == "true"
STRICT = IAM and SIG and os.environ.get("LAB_S3AUTH") == "true"
ACCT = "000000000000"
REGION = "us-east-1"
DENIED = ("AccessDenied", "AccessDeniedException")

lam, iam, logs = c("lambda"), c("iam"), c("logs")

LOGS_ALLOW = allow(["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"])


def zip_code(src, name="app.py"):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(name, src)
    return buf.getvalue()


def role(name, *stmts):
    """lambda.amazonaws.com이 assume하는 실행 role. stmts가 비면 정책 없음."""
    arn = iam.create_role(RoleName=name, AssumeRolePolicyDocument=policy(
        {"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}))["Role"]["Arn"]
    if stmts:
        iam.put_role_policy(RoleName=name, PolicyName="p", PolicyDocument=policy(*stmts))
    return arn


def function(name, src, role_arn, timeout=15, env=None, **kw):
    lam.create_function(FunctionName=name, Runtime="python3.12", Handler="app.handler", Role=role_arn,
                        Code={"ZipFile": zip_code(src)}, Timeout=timeout,
                        Environment={"Variables": env or {}}, **kw)
    wait_until(lambda: lam.get_function(FunctionName=name)["Configuration"]["State"] == "Active", 120)
    return lam.get_function(FunctionName=name)["Configuration"]["FunctionArn"]


def invoke(client, name, payload=None, **kw):
    """(호출 결과 코드, 응답 payload dict 또는 None, FunctionError, 경과 초)"""
    t0 = time.time()
    r, d = outcome(client.invoke, FunctionName=name, Payload=json.dumps(payload or {}).encode(), **kw)
    dt = time.time() - t0
    if r != "ALLOW":
        return r, d, None, dt
    body = d["Payload"].read()
    try:
        body = json.loads(body)
    except Exception:
        body = body.decode(errors="replace")
    return r, body, d.get("FunctionError"), dt


def find_logs(group, needle, timeout=40, client=None):
    """group의 log event 중 needle을 포함하는 message 목록. 없으면 timeout까지 poll."""
    cl = client or logs
    found = []

    def poll():
        nonlocal found
        r, d = outcome(cl.filter_log_events, logGroupName=group, filterPattern=f'"{needle}"')
        if r != "ALLOW":
            found = r
            return True  # 권한 거부 등은 즉시 반환
        found = [e["message"] for e in d.get("events", [])]
        return bool(found)

    wait_until(poll, timeout, 2)
    return found


def all_logs(group, timeout=5):
    r, d = outcome(logs.filter_log_events, logGroupName=group)
    return [e["message"] for e in d.get("events", [])] if r == "ALLOW" else []


def uid():
    return uuid.uuid4().hex[:8]
