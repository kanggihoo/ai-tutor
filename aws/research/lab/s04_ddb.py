"""s04 (W2, W3a) Lambda 실행 role -> DynamoDB, 조건부 쓰기.

W2 같은 handler·table·입력, 실행 role만 다르게: Allow 없음 / PutItem Allow / Allow + 명시 Deny.
   Invoke 결과(호출 성공)와 handler 안 PutItem 결과를 따로 본다. handler는 자기 신원(GetCallerIdentity)도 돌려준다.
W3a 조건 없는 같은 key PutItem 두 번(덮어씀) vs attribute_not_exists 조건(두 번째 거부),
    동시 5개 조건부 insert(1개만 성공), 상태 전이 PENDING->PAID 조건부 update 두 번(적용 1회).

AWS 기대값: https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html
           https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ConditionExpressions.html
"""
import threading

from botocore.exceptions import ClientError

from lib import Checker, allow, c, deny, make_user, policy
from sl import DENIED, IAM, LOGS_ALLOW, function, invoke, lam, role

ck = Checker("s04")
ddb = c("dynamodb")
ddb.create_table(TableName="Orders", AttributeDefinitions=[{"AttributeName": "orderId", "AttributeType": "S"}],
                 KeySchema=[{"AttributeName": "orderId", "KeyType": "HASH"}], BillingMode="PAY_PER_REQUEST")
TARN = "arn:aws:dynamodb:us-east-1:000000000000:table/Orders"
SRC = r'''
import boto3
from botocore.exceptions import ClientError
def handler(event, context):
    who = boto3.client("sts").get_caller_identity()["Arn"]
    try:
        boto3.client("dynamodb").put_item(TableName="Orders", Item={"orderId": {"S": event["orderId"]}, "by": {"S": who}})
        return {"put": "OK", "who": who}
    except ClientError as e:
        return {"put": e.response["Error"]["Code"], "who": who}
'''
# ---------- W2 ----------
cases = {
    "none": role("ddb-none", LOGS_ALLOW),
    "allow": role("ddb-allow", LOGS_ALLOW, allow("dynamodb:PutItem", TARN)),
    "deny": role("ddb-deny", LOGS_ALLOW, allow("dynamodb:PutItem", TARN), deny("dynamodb:PutItem", TARN)),
}
expect = {"none": DENIED if IAM else "OK", "allow": "OK", "deny": DENIED if IAM else "OK"}
for k, arn in cases.items():
    function(f"put-{k}", SRC, arn)
    r, body, ferr, _ = invoke(lam, f"put-{k}", {"orderId": f"w2-{k}"})
    ck.check(f"W2.{k}.invoke", r, "ALLOW", body)
    ck.check(f"W2.{k}.handler-PutItem", body.get("put") if isinstance(body, dict) else body, expect[k], body)
    ck.check(f"W2.{k}.handler-identity", (body.get("who") or "").startswith(f"arn:aws:sts::000000000000:assumed-role/ddb-{k}/"), True, body)
    item = ddb.get_item(TableName="Orders", Key={"orderId": {"S": f"w2-{k}"}}).get("Item")
    ck.check(f"W2.{k}.item-exists", item is not None, expect[k] == "OK", item)

# ---------- W3a ----------
dev = make_user("dev", policy(allow("dynamodb:*", TARN)))
D = c("dynamodb", **dev)


def put(oid, amount, cond=False):
    kw = {"ConditionExpression": "attribute_not_exists(orderId)"} if cond else {}
    try:
        D.put_item(TableName="Orders", Item={"orderId": {"S": oid}, "amount": {"N": str(amount)}}, **kw)
        return "OK"
    except ClientError as e:
        return e.response["Error"]["Code"]


def amount(oid):
    return D.get_item(TableName="Orders", Key={"orderId": {"S": oid}}, ConsistentRead=True)["Item"]["amount"]["N"]


ck.check("W3a.plain.first", put("o-1", 100), "OK")
ck.check("W3a.plain.second(overwrites)", put("o-1", 999), "OK")
ck.check("W3a.plain.final-amount", amount("o-1"), "999")
ck.check("W3a.cond.first", put("o-2", 100, cond=True), "OK")
ck.check("W3a.cond.second", put("o-2", 999, cond=True), "ConditionalCheckFailedException")
ck.check("W3a.cond.final-amount", amount("o-2"), "100")
res = []
ts = [threading.Thread(target=lambda a=a: res.append(put("o-3", a, cond=True))) for a in range(1, 6)]
[t.start() for t in ts]
[t.join() for t in ts]
ck.check("W3a.concurrent5.OK-count", res.count("OK"), 1, res)
ck.check("W3a.concurrent5.failed-count", res.count("ConditionalCheckFailedException"), 4, res)

D.put_item(TableName="Orders", Item={"orderId": {"S": "o-17"}, "status": {"S": "PENDING"}, "applied": {"N": "0"}})


def pay():
    try:
        D.update_item(TableName="Orders", Key={"orderId": {"S": "o-17"}},
                      UpdateExpression="SET #s = :paid ADD applied :one",
                      ConditionExpression="#s = :pending",
                      ExpressionAttributeNames={"#s": "status"},
                      ExpressionAttributeValues={":paid": {"S": "PAID"}, ":pending": {"S": "PENDING"}, ":one": {"N": "1"}})
        return "OK"
    except ClientError as e:
        return e.response["Error"]["Code"]


ck.check("W3a.transition.first", pay(), "OK")
ck.check("W3a.transition.second", pay(), "ConditionalCheckFailedException")
it = D.get_item(TableName="Orders", Key={"orderId": {"S": "o-17"}}, ConsistentRead=True)["Item"]
ck.check("W3a.transition.final", f'{it["status"]["S"]}/{it["applied"]["N"]}', "PAID/1", it)

ck.done()
