"""s05 (W8 + D 최소 중복 확인) strict에서 Lambda 동시성·async 재시도·SQS ESM.

W8a reserved concurrency 1, learner가 겹친 호출 3개 -> ALLOW 1 / TooManyRequestsException 2. 해제 후 3 ALLOW
W8b async 실패 MaximumRetryAttempts 2 vs 0 -> OnFailure(SQS) 레코드 approximateInvokeCount 3 vs 1
    실행 role의 sqs:SendMessage 유/무 (AWS: 없으면 destination 전달 실패)
W8c SQS ESM: 실행 role의 queue 소비 권한 유/무 (AWS: 없으면 CreateEventSourceMapping이 거부)
    성공 함수 -> main 0 / DLQ 0, 실패 함수 -> VisibilityTimeout 뒤 재수신 -> maxReceiveCount 뒤 DLQ 1
D   worker가 조건부 상태 전이(PENDING->PAID, applied+1). 첫 수신에서 쓰기 후 일부러 실패 -> 재수신 -> 이미 PAID면 완료로 처리.
    같은 orderId 메시지 두 번 -> applied 1. handler 호출 수와 업무 적용 수를 구분

AWS 기대값: https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html
           https://docs.aws.amazon.com/lambda/latest/dg/invocation-async-retain-records.html (destination 권한)
           https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html (실행 role 권한, 재수신)
"""
import json
import threading
import time

from lib import Checker, allow, c, make_user, outcome, policy, wait_until
from sl import IAM, LOGS_ALLOW, find_logs, function, invoke, lam, role, uid

ck = Checker("s05")
sqs, ddb = c("sqs"), c("dynamodb")


def q(name, **attrs):
    url = sqs.create_queue(QueueName=name, Attributes={k: str(v) for k, v in attrs.items()})["QueueUrl"]
    return url, sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]


def count(url):
    a = sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["ApproximateNumberOfMessages", "ApproximateNumberOfMessagesNotVisible"])["Attributes"]
    return int(a["ApproximateNumberOfMessages"]) + int(a["ApproximateNumberOfMessagesNotVisible"])


def recv(url, wait=60):
    m = wait_until(lambda: sqs.receive_message(QueueUrl=url, MaxNumberOfMessages=1, WaitTimeSeconds=2).get("Messages"), wait)
    if m:
        sqs.delete_message(QueueUrl=url, ReceiptHandle=m[0]["ReceiptHandle"])
        return json.loads(m[0]["Body"])
    return None


SRC = r'''
import json, os, time, boto3
from botocore.exceptions import ClientError
def handler(event, context):
    if isinstance(event, dict) and event.get("mode") == "sleep":
        time.sleep(4); return "slept"
    if isinstance(event, dict) and event.get("mode") == "fail":
        raise Exception("async-fail")
    if isinstance(event, dict) and "Records" in event:
        for rec in event["Records"]:
            body = json.loads(rec["body"])
            n = rec["attributes"]["ApproximateReceiveCount"]
            print("WORKER " + body.get("orderId", "?") + " receive=" + n)
            if os.environ.get("MODE") == "fail":
                raise Exception("worker-fail")
            if os.environ.get("MODE") == "pay":
                t = boto3.client("dynamodb")
                try:
                    t.update_item(TableName="Orders", Key={"orderId": {"S": body["orderId"]}},
                        UpdateExpression="SET #s = :paid ADD applied :one", ConditionExpression="#s = :pending",
                        ExpressionAttributeNames={"#s": "status"},
                        ExpressionAttributeValues={":paid": {"S": "PAID"}, ":pending": {"S": "PENDING"}, ":one": {"N": "1"}})
                    print("APPLIED " + body["orderId"])
                except ClientError as e:
                    if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                        raise
                    st = t.get_item(TableName="Orders", Key={"orderId": {"S": body["orderId"]}}, ConsistentRead=True)["Item"]["status"]["S"]
                    if st != "PAID":
                        raise
                    print("ALREADY " + body["orderId"])
                if body.get("crashOnce") and n == "1":
                    raise Exception("crash-after-write")
    return {"ok": True}
'''

# ---------- W8a ----------
fa = function("conc", SRC, role("conc-role", LOGS_ALLOW))
dev = make_user("dev", policy(allow("lambda:InvokeFunction", "*")))
L = c("lambda", **dev)
invoke(L, "conc", {})


def burst():
    res = []
    ts = [threading.Thread(target=lambda: res.append(invoke(L, "conc", {"mode": "sleep"})[0])) for _ in range(3)]
    for t in ts:
        t.start(); time.sleep(0.2)
    [t.join() for t in ts]
    return res


lam.put_function_concurrency(FunctionName="conc", ReservedConcurrentExecutions=1)
res = burst()
ck.check("W8a.reserved1.ALLOW", res.count("ALLOW"), 1, res)
ck.check("W8a.reserved1.throttled", res.count("TooManyRequestsException"), 2, res)
lam.delete_function_concurrency(FunctionName="conc")
res = burst()
ck.check("W8a.no-reservation.ALLOW", res.count("ALLOW"), 3, res)

# ---------- W8b ----------
dest_url, dest_arn = q("onfailure")
for k, stmts in {"with": [LOGS_ALLOW, allow("sqs:SendMessage", dest_arn)], "without": [LOGS_ALLOW]}.items():
    function(f"af-{k}", SRC, role(f"af-{k}-role", *stmts))
    lam.put_function_event_invoke_config(FunctionName=f"af-{k}", MaximumRetryAttempts=2,
                                         DestinationConfig={"OnFailure": {"Destination": dest_arn}})
    lam.invoke(FunctionName=f"af-{k}", InvocationType="Event", Payload=json.dumps({"mode": "fail"}).encode())
    rec = recv(dest_url, 45)
    got = (rec or {}).get("requestContext", {}).get("approximateInvokeCount")
    if k == "with":
        ck.check("W8b.role-with-SendMessage.retries2.approximateInvokeCount", got, 3, rec)
    else:
        ck.check("W8b.role-without-SendMessage.record-delivered(AWS: no)", got is not None, True, rec,
                 aws_diff=IAM, doc="lambda.md: destination 전달 시 실행 role 권한 검사 언급 없음")
lam.put_function_event_invoke_config(FunctionName="af-with", MaximumRetryAttempts=0,
                                     DestinationConfig={"OnFailure": {"Destination": dest_arn}})
lam.invoke(FunctionName="af-with", InvocationType="Event", Payload=json.dumps({"mode": "fail"}).encode())
rec = recv(dest_url, 45)
ck.check("W8b.retries0.approximateInvokeCount", (rec or {}).get("requestContext", {}).get("approximateInvokeCount"), 1, rec)

# ---------- W8c ----------
def consume_stmt(arn):
    return allow(["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"], arn)


nop_url, nop_arn = q("noperm-main")
function("w-noperm", SRC, role("w-noperm-role", LOGS_ALLOW))
r, d = outcome(lam.create_event_source_mapping, FunctionName="w-noperm", EventSourceArn=nop_arn, BatchSize=1)
ck.info(f"ESM without queue permission: {r} {str(d)[:160] if r != 'ALLOW' else ''}")
if r == "ALLOW":
    sqs.send_message(QueueUrl=nop_url, MessageBody=json.dumps({"orderId": "np-1"}))
    consumed = wait_until(lambda: count(nop_url) == 0, 25)
    ck.check("W8c.role-without-queue-perms.ESM-created(AWS: rejected)", r, "ALLOW", aws_diff=IAM,
             doc="lambda.md: ESM 생성 시 실행 role 권한 검사 언급 없음")
    ck.check("W8c.role-without-queue-perms.message-consumed(AWS: no)", bool(consumed), True, aws_diff=IAM)
else:
    ck.check("W8c.role-without-queue-perms.ESM-created", r, "InvalidParameterValueException", d)


def esm(prefix, mode, extra=()):
    dlq_u, dlq_a = q(f"{prefix}-dlq")
    main_u, main_a = q(f"{prefix}-main", VisibilityTimeout=3,
                       RedrivePolicy=json.dumps({"deadLetterTargetArn": dlq_a, "maxReceiveCount": 3}))
    function(f"{prefix}-fn", SRC, role(f"{prefix}-role", LOGS_ALLOW, consume_stmt(main_a), *extra), env={"MODE": mode})
    lam.create_event_source_mapping(FunctionName=f"{prefix}-fn", EventSourceArn=main_a, BatchSize=1)
    return main_u, dlq_u


main_u, dlq_u = esm("ok", "ok")
sqs.send_message(QueueUrl=main_u, MessageBody=json.dumps({"orderId": "ok-1"}))
wait_until(lambda: count(main_u) == 0, 40); time.sleep(8)
ck.check("W8c.success.main/dlq", f"{count(main_u)}/{count(dlq_u)}", "0/0")
main_u, dlq_u = esm("bad", "fail")
sqs.send_message(QueueUrl=main_u, MessageBody=json.dumps({"orderId": "bad-1"}))
wait_until(lambda: count(dlq_u) >= 1, 90)
ck.check("W8c.failure.main/dlq", f"{count(main_u)}/{count(dlq_u)}", "0/1")
w = find_logs("/aws/lambda/bad-fn", "WORKER bad-1", timeout=10)
ck.check("W8c.failure.handler-calls(=maxReceiveCount 3)", len(w) if isinstance(w, list) else w, 3, w)

# ---------- D ----------
ddb.create_table(TableName="Orders", AttributeDefinitions=[{"AttributeName": "orderId", "AttributeType": "S"}],
                 KeySchema=[{"AttributeName": "orderId", "KeyType": "HASH"}], BillingMode="PAY_PER_REQUEST")
TARN = "arn:aws:dynamodb:us-east-1:000000000000:table/Orders"
for oid in ("o-17", "o-18"):
    ddb.put_item(TableName="Orders", Item={"orderId": {"S": oid}, "status": {"S": "PENDING"}, "applied": {"N": "0"}})
main_u, dlq_u = esm("pay", "pay", extra=(allow(["dynamodb:UpdateItem", "dynamodb:GetItem"], TARN),))
sqs.send_message(QueueUrl=main_u, MessageBody=json.dumps({"orderId": "o-17", "crashOnce": True}))
for _ in range(2):
    sqs.send_message(QueueUrl=main_u, MessageBody=json.dumps({"orderId": "o-18"}))
wait_until(lambda: count(main_u) == 0, 60); time.sleep(8)


def item(oid):
    it = ddb.get_item(TableName="Orders", Key={"orderId": {"S": oid}}, ConsistentRead=True)["Item"]
    return f'{it["status"]["S"]}/{it["applied"]["N"]}'


G = "/aws/lambda/pay-fn"
calls17 = find_logs(G, "WORKER o-17", timeout=10)
calls18 = find_logs(G, "WORKER o-18", timeout=10)
ck.check("D.crash-after-write.item(status/applied)", item("o-17"), "PAID/1")
ck.check("D.crash-after-write.handler-calls", len(calls17) if isinstance(calls17, list) else calls17, 2, calls17)
ck.check("D.duplicate-message.item(status/applied)", item("o-18"), "PAID/1")
ck.check("D.duplicate-message.handler-calls", len(calls18) if isinstance(calls18, list) else calls18, 2, calls18)
ck.check("D.main/dlq", f"{count(main_u)}/{count(dlq_u)}", "0/0")

ck.done()
