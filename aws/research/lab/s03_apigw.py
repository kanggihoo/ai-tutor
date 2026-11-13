"""s03 (W1) API Gateway REST v1 AWS_PROXY -> Lambda.

데이터 경로: path parameter / query / header / body 가 event로 전달되는가, 정상 proxy 응답이 그대로 나가는가
오류 층: handler 예외 -> 502, 잘못된 proxy 응답 -> 502, API Gateway는 재시도하지 않음(handler 1회)
인가: 함수 policy(AddPermission) 없음 / 맞는 SourceArn / 다른 API의 SourceArn. AWS는 없거나 틀리면 500, handler 미호출

AWS 기대값: https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway-errors.html
           https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
           https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html (resource-based policy)
"""
import json
import time

import requests

from lib import Checker, c
from sl import IAM, LOGS_ALLOW, function, find_logs, lam, role, uid

ck = Checker("s03")
apigw = c("apigateway")
SRC = r'''
import json
def handler(event, context):
    mark = (event.get("headers") or {}).get("X-Mark") or (event.get("headers") or {}).get("x-mark")
    print("HANDLED " + str(mark))
    mode = (event.get("queryStringParameters") or {}).get("mode")
    if mode == "raise":
        raise RuntimeError("boom")
    if mode == "bad":
        return "this is not a proxy response"
    return {"statusCode": 201, "headers": {"X-From": "lambda"},
            "body": json.dumps({"path": event.get("path"), "id": (event.get("pathParameters") or {}).get("id"),
                                "q": event.get("queryStringParameters"), "body": event.get("body"),
                                "method": event.get("httpMethod"), "mark": mark})}
'''
fn_arn = function("orders", SRC, role("orders-role", LOGS_ALLOW))


def make_api(name):
    api = apigw.create_rest_api(name=name)["id"]
    root = [r for r in apigw.get_resources(restApiId=api)["items"] if r["path"] == "/"][0]["id"]
    orders = apigw.create_resource(restApiId=api, parentId=root, pathPart="orders")["id"]
    oid = apigw.create_resource(restApiId=api, parentId=orders, pathPart="{id}")["id"]
    apigw.put_method(restApiId=api, resourceId=oid, httpMethod="POST", authorizationType="NONE")
    apigw.put_integration(restApiId=api, resourceId=oid, httpMethod="POST", type="AWS_PROXY", integrationHttpMethod="POST",
                          uri=f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{fn_arn}/invocations")
    apigw.create_deployment(restApiId=api, stageName="dev")
    return api


api = make_api("orders-api")
other = make_api("other-api")
URL = f"http://floci:4566/restapis/{api}/dev/_user_request_/orders/o-17"


def call(mode=None):
    m = uid()
    params = {"mode": mode} if mode else {"src": "web"}
    r = requests.post(URL, params=params, headers={"X-Mark": m, "Content-Type": "application/json"},
                      data=json.dumps({"qty": 2}), timeout=30)
    return r, m


def handled(mark, timeout=15):
    hits = find_logs("/aws/lambda/orders", "HANDLED " + mark, timeout=timeout)
    return len(hits) if isinstance(hits, list) else hits


# ---------- 인가: 함수 policy 없음 ----------
r, m = call()
n = handled(m, timeout=10)
ck.info(f"no-permission: status={r.status_code} body={r.text[:120]} handler-calls={n}")
ck.check("W1.no-function-policy.status(AWS: 500)", r.status_code, 201, r.text[:200], aws_diff=True,
         doc="api-gateway.md: Lambda 호출 권한(AddPermission) 검사 언급 없음")
ck.check("W1.no-function-policy.handler-called(AWS: 0)", n, 1, aws_diff=True)

# 다른 API의 SourceArn만 허용
lam.add_permission(FunctionName="orders", StatementId="other-api", Action="lambda:InvokeFunction",
                   Principal="apigateway.amazonaws.com", SourceArn=f"arn:aws:execute-api:us-east-1:000000000000:{other}/*/POST/orders/*")
r, m = call()
ck.check("W1.wrong-SourceArn.status(AWS: 500)", r.status_code, 201, r.text[:200], aws_diff=True)
lam.add_permission(FunctionName="orders", StatementId="this-api", Action="lambda:InvokeFunction",
                   Principal="apigateway.amazonaws.com", SourceArn=f"arn:aws:execute-api:us-east-1:000000000000:{api}/*/POST/orders/*")
r, m = call()
ck.check("W1.right-SourceArn.status", r.status_code, 201, r.text[:200])

# ---------- 데이터 경로 ----------
body = r.json()
ck.check("W1.data.pathParameters.id", body.get("id"), "o-17", body)
ck.check("W1.data.path", body.get("path"), "/orders/o-17", body)
ck.check("W1.data.query", (body.get("q") or {}).get("src"), "web", body)
ck.check("W1.data.header(sent X-Mark echoed)", body.get("mark") == m, True, body)
ck.check("W1.data.body(string)", body.get("body"), json.dumps({"qty": 2}), body)
ck.check("W1.data.method", body.get("method"), "POST", body)
ck.check("W1.resp.status-from-lambda(201)", r.status_code, 201)
ck.check("W1.resp.header-from-lambda", r.headers.get("X-From"), "lambda", dict(r.headers))

# ---------- 오류 층 ----------
r, m = call("raise")
ck.check("W1.handler-raise.status", r.status_code, 502, r.text[:200])
time.sleep(3)
ck.check("W1.handler-raise.handler-calls(no retry)", handled(m), 1)
ck.info(f"raise body={r.text[:160]}")
r, m = call("bad")
# 문서: malformed proxy payload -> INTEGRATION_FAILURE(502). 실제: 문자열을 돌려주면 200, 빈 body
ck.check("W1.bad-proxy-response.status(AWS·doc: 502)", r.status_code, 200, r.text[:200], doc_diff=True,
         doc="api-gateway.md:393 'Lambda proxy function error, malformed proxy payload, or missing function | INTEGRATION_FAILURE'")
ck.info(f"bad body={r.text[:160]}")

ck.done()
