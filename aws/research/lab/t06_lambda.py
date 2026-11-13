"""T06 Lambda가 managed service로서 갖는 의미: 동시성 예약, 비동기 재시도/목적지/DLQ, SQS ESM과 visibility timeout.

E1 reserved concurrency: 예약 1이면 동시에 3개 부를 때 몇 개가 429인가 (예약 없음과 대조, 예약 0 대조)
E2 비동기 호출 실패: MaximumRetryAttempts 2 vs 0 -> OnFailure 레코드의 approximateInvokeCount, DLQ 레코드
E3 SQS event source mapping: 함수가 실패하면 VisibilityTimeout 뒤 재수신 -> maxReceiveCount 뒤 DLQ (성공 함수와 대조)

AWS 기대값: https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html
           https://docs.aws.amazon.com/lambda/latest/dg/invocation-async-retain-records.html
           https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-errorhandling.html
"""
import io
import json
import threading
import time
import zipfile

from lib import Checker, c, outcome, policy, wait_until

ck = Checker("t06")
lam, sqs, iam = c("lambda"), c("sqs"), c("iam")

CODE = r'''
import os, time
def handler(event, context):
    if isinstance(event, dict) and event.get("mode") == "sleep":
        time.sleep(event.get("s", 4)); return {"slept": True}
    if isinstance(event, dict) and event.get("mode") == "fail":
        raise Exception("boom-on-purpose")
    if isinstance(event, dict) and "Records" in event and os.environ.get("FAIL_SQS") == "1":
        raise Exception("sqs-boom")
    return {"ok": True}
'''
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as z:
    z.writestr("app.py", CODE)
ZIP = buf.getvalue()
role = iam.create_role(RoleName="lambda-exec", AssumeRolePolicyDocument=policy(
    {"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}))["Role"]["Arn"]


def fn(name, env=None, **kw):
    lam.create_function(FunctionName=name, Runtime="python3.12", Handler="app.handler", Role=role,
                        Code={"ZipFile": ZIP}, Timeout=15, Environment={"Variables": env or {}}, **kw)
    wait_until(lambda: lam.get_function(FunctionName=name)["Configuration"]["State"] == "Active", 120)
    return lam.get_function(FunctionName=name)["Configuration"]["FunctionArn"]


def q(name, **attrs):
    url = sqs.create_queue(QueueName=name, Attributes={k: str(v) for k, v in attrs.items()})["QueueUrl"]
    arn = sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]
    return url, arn


def count(url):
    a = sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["ApproximateNumberOfMessages", "ApproximateNumberOfMessagesNotVisible"])["Attributes"]
    return int(a["ApproximateNumberOfMessages"]) + int(a["ApproximateNumberOfMessagesNotVisible"])


# ---------- E1 ----------
fn("conc")
r, d = outcome(lam.invoke, FunctionName="conc", Payload=b"{}")
ck.check("E1.warmup-invoke", r, "ALLOW", d)


def burst(n=3):
    res = []
    def one():
        res.append(outcome(lam.invoke, FunctionName="conc", Payload=json.dumps({"mode": "sleep", "s": 5}).encode())[0])
    ts = [threading.Thread(target=one) for _ in range(n)]
    for t in ts:
        t.start()
        time.sleep(0.2)
    for t in ts:
        t.join()
    return sorted(res)


lam.put_function_concurrency(FunctionName="conc", ReservedConcurrentExecutions=1)
res = burst()
ck.check("E1.reserved=1,burst=3 -> ALLOW count", res.count("ALLOW"), 1, res)
ck.check("E1.reserved=1,burst=3 -> TooManyRequestsException count", res.count("TooManyRequestsException"), 2, res)
lam.delete_function_concurrency(FunctionName="conc")
res = burst()
ck.check("E1.no-reservation,burst=3 -> ALLOW count", res.count("ALLOW"), 3, res)
lam.put_function_concurrency(FunctionName="conc", ReservedConcurrentExecutions=0)
r, d = outcome(lam.invoke, FunctionName="conc", Payload=b"{}")
ck.check("E1.reserved=0 -> invoke", r, "TooManyRequestsException", d)
r, d = outcome(lam.put_function_concurrency, FunctionName="conc", ReservedConcurrentExecutions=950)
ck.check("E1.reserve 950 of 1000 (must leave 100 unreserved)", r, ("InvalidParameterValueException", "LimitExceededException"), d)

# ---------- E2 ----------
fail_url, fail_arn = q("onfailure-dest")
fn("async-fail")
lam.put_function_event_invoke_config(FunctionName="async-fail", MaximumRetryAttempts=2,
                                     DestinationConfig={"OnFailure": {"Destination": fail_arn}})
lam.invoke(FunctionName="async-fail", InvocationType="Event", Payload=json.dumps({"mode": "fail"}).encode())


def recv(url, wait=60):
    m = wait_until(lambda: sqs.receive_message(QueueUrl=url, MaxNumberOfMessages=1, WaitTimeSeconds=2,
                                               MessageAttributeNames=["All"]).get("Messages"), wait)
    return m[0] if m else None


m = recv(fail_url)
rec = json.loads(m["Body"]) if m else {}
ck.check("E2.retries=2 -> OnFailure.condition", rec.get("requestContext", {}).get("condition"), "RetriesExhausted", rec)
ck.check("E2.retries=2 -> approximateInvokeCount", rec.get("requestContext", {}).get("approximateInvokeCount"), 3, rec)
if m:
    sqs.delete_message(QueueUrl=fail_url, ReceiptHandle=m["ReceiptHandle"])
lam.put_function_event_invoke_config(FunctionName="async-fail", MaximumRetryAttempts=0,
                                     DestinationConfig={"OnFailure": {"Destination": fail_arn}})
lam.invoke(FunctionName="async-fail", InvocationType="Event", Payload=json.dumps({"mode": "fail"}).encode())
m = recv(fail_url)
rec = json.loads(m["Body"]) if m else {}
ck.check("E2.retries=0 -> approximateInvokeCount", rec.get("requestContext", {}).get("approximateInvokeCount"), 1, rec)

dlq_url, dlq_arn = q("fn-dlq")
fn("async-dlq", DeadLetterConfig={"TargetArn": dlq_arn})
lam.put_function_event_invoke_config(FunctionName="async-dlq", MaximumRetryAttempts=0)
lam.invoke(FunctionName="async-dlq", InvocationType="Event", Payload=json.dumps({"mode": "fail", "id": "x1"}).encode())
m = recv(dlq_url)
attrs = {k: v.get("StringValue") for k, v in (m or {}).get("MessageAttributes", {}).items()}
ck.check("E2.DLQ.body=original-payload", json.loads(m["Body"]).get("id") if m else None, "x1", m)
ck.check("E2.DLQ.ErrorMessage-attr", "boom-on-purpose" in (attrs.get("ErrorMessage") or ""), True, attrs)

# ---------- E3 ----------
def esm_case(prefix, fail):
    dlq_u, dlq_a = q(f"{prefix}-dlq")
    main_u, main_a = q(f"{prefix}-main", VisibilityTimeout=3,
                       RedrivePolicy=json.dumps({"deadLetterTargetArn": dlq_a, "maxReceiveCount": 2}))
    fn(f"{prefix}-fn", env={"FAIL_SQS": "1" if fail else "0"})
    lam.create_event_source_mapping(FunctionName=f"{prefix}-fn", EventSourceArn=main_a, BatchSize=1)
    sqs.send_message(QueueUrl=main_u, MessageBody="order-1")
    t0 = time.time()
    if fail:
        wait_until(lambda: count(dlq_u) >= 1, 90)
    else:
        wait_until(lambda: count(main_u) == 0, 60)
        time.sleep(8)  # 재수신이 있었다면 DLQ로 갈 시간
    return count(main_u), count(dlq_u), round(time.time() - t0)


main_n, dlq_n, secs = esm_case("ok", fail=False)
ck.check("E3.success-fn -> main/dlq counts", f"{main_n}/{dlq_n}", "0/0")
main_n, dlq_n, secs = esm_case("bad", fail=True)
ck.info(f"failing fn: message reached DLQ after ~{secs}s (VisibilityTimeout=3, maxReceiveCount=2)")
ck.check("E3.failing-fn -> main/dlq counts", f"{main_n}/{dlq_n}", "0/1")

ck.done()
