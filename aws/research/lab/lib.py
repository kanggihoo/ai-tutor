"""실험 공통 도구.

- c(): floci에 붙는 boto3 client. 재시도는 끈다(에러 코드를 그대로 보려고).
- outcome(): 호출 결과를 "ALLOW" 또는 에러 코드 문자열(예: "AccessDenied")로 바꾼다.
- Checker: 기대값과 실제값을 한 줄씩 찍고, 하나라도 어긋나면 exit 1.
  doc_diff=True인 check는 "floci 문서 주장과 실제가 다르다"는 것을 이미 확인한 항목이다.
  aws_diff=True인 check는 floci 문서는 말이 없고, AWS 문서의 동작과 실제가 다른 항목이다.
  두 경우 모두 expected는 관측값으로 고정해 회귀를 잡고, 주장은 doc 인자에 따로 남긴다.
"""
import json
import os
import sys
import time

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

EP = os.environ.get("AWS_ENDPOINT_URL", "http://floci:4566")
MODE = os.environ.get("LAB_MODE", "")
CFG = Config(retries={"max_attempts": 1, "mode": "standard"}, connect_timeout=5, read_timeout=60)


def c(svc, key="test", secret="test", token=None, region="us-east-1"):
    return boto3.client(
        svc,
        endpoint_url=EP,
        region_name=region,
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        aws_session_token=token,
        config=CFG,
    )


def creds_of(d):
    """AssumeRole 등의 Credentials dict -> c()에 넘길 kwargs"""
    return dict(key=d["AccessKeyId"], secret=d["SecretAccessKey"], token=d.get("SessionToken"))


def outcome(fn, *a, **kw):
    try:
        r = fn(*a, **kw)
        return "ALLOW", r
    except ClientError as e:
        err = e.response.get("Error", {})
        code = err.get("Code") or str(e.response.get("ResponseMetadata", {}).get("HTTPStatusCode"))
        status = e.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        return f"{code}", {"status": status, "message": (err.get("Message") or "")[:160]}


def policy(*stmts):
    return json.dumps({"Version": "2012-10-17", "Statement": list(stmts)})


def allow(action, resource="*", **extra):
    s = {"Effect": "Allow", "Action": action, "Resource": resource}
    s.update(extra)
    return s


def deny(action, resource="*", **extra):
    s = {"Effect": "Deny", "Action": action, "Resource": resource}
    s.update(extra)
    return s


def make_user(name, inline=None, boundary_arn=None, iam=None):
    """IAM user + access key. inline: policy JSON 문자열."""
    iam = iam or c("iam")
    kw = {"UserName": name}
    if boundary_arn:
        kw["PermissionsBoundary"] = boundary_arn
    iam.create_user(**kw)
    if inline:
        iam.put_user_policy(UserName=name, PolicyName=f"{name}-inline", PolicyDocument=inline)
    k = iam.create_access_key(UserName=name)["AccessKey"]
    return dict(key=k["AccessKeyId"], secret=k["SecretAccessKey"])


def wait_until(fn, timeout=60, interval=1.0):
    end = time.time() + timeout
    last = None
    while time.time() < end:
        last = fn()
        if last:
            return last
        time.sleep(interval)
    return last


class Checker:
    def __init__(self, exp):
        self.exp = exp
        self.fail = 0
        print(f"=== {exp} MODE={MODE or '-'}")

    def check(self, name, actual, expected, detail=None, doc=None, doc_diff=False, aws_diff=False):
        ok = actual in expected if isinstance(expected, (set, tuple, list)) else actual == expected
        tag = "OK" if ok else "MISMATCH"
        if doc_diff:
            tag += " DOC-DIFF"
        if aws_diff:
            tag += " AWS-DIFF"
        line = f"CHECK {self.exp}[{MODE}] {name} expected={expected} actual={actual} {tag}"
        if doc:
            line += f" | doc: {doc}"
        print(line)
        if detail is not None and (not ok or os.environ.get("LAB_VERBOSE")):
            print(f"      detail: {json.dumps(detail, default=str)[:400]}")
        if not ok:
            self.fail += 1
        return ok

    def info(self, msg):
        print(f"INFO  {msg}")

    def done(self):
        print(f"RESULT {self.exp}[{MODE}] {'PASS' if self.fail == 0 else 'FAIL'} mismatches={self.fail}")
        sys.exit(0 if self.fail == 0 else 1)
