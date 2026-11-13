"""T09 Cognito user pool -> API Gateway REST authorizer, 그리고 AWS_IAM 메서드.

E1 COGNITO_USER_POOLS authorizer: 토큰 없음 / 엉터리 / 다른 pool의 토큰 / 올바른 IdToken (NONE 메서드와 대조)
E2 AWS_IAM 메서드: 서명 없음 / test key 서명 / 정책 없는 user 서명 (IAM on에서 AWS는 403)

LAB_IAM=true|false 대조.
AWS 기대값: https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html
           https://docs.aws.amazon.com/apigateway/latest/developerguide/permissions.html
"""
import os

import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

from lib import Checker, c, make_user

IAM = os.environ.get("LAB_IAM") == "true"
ck = Checker("t09")
cog, apigw = c("cognito-idp"), c("apigateway")


def pool_with_user(name, user):
    pid = cog.create_user_pool(PoolName=name)["UserPool"]["Id"]
    parn = cog.describe_user_pool(UserPoolId=pid)["UserPool"]["Arn"]
    cid = cog.create_user_pool_client(UserPoolId=pid, ClientName="web", GenerateSecret=False,
                                      ExplicitAuthFlows=["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"])["UserPoolClient"]["ClientId"]
    cog.admin_create_user(UserPoolId=pid, Username=user, MessageAction="SUPPRESS")
    cog.admin_set_user_password(UserPoolId=pid, Username=user, Password="Passw0rd!Lab", Permanent=True)
    tok = cog.initiate_auth(ClientId=cid, AuthFlow="USER_PASSWORD_AUTH",
                            AuthParameters={"USERNAME": user, "PASSWORD": "Passw0rd!Lab"})["AuthenticationResult"]
    return pid, parn, tok


pid, parn, tok = pool_with_user("main-pool", "kim")
_, _, other_tok = pool_with_user("other-pool", "lee")

api = apigw.create_rest_api(name="lab-api")["id"]
root = [r for r in apigw.get_resources(restApiId=api)["items"] if r["path"] == "/"][0]["id"]
auth_id = apigw.create_authorizer(restApiId=api, name="cog", type="COGNITO_USER_POOLS", providerARNs=[parn],
                                  identitySource="method.request.header.Authorization")["id"]


def mock_method(path, auth_type, authorizer=None):
    rid = apigw.create_resource(restApiId=api, parentId=root, pathPart=path)["id"]
    kw = {"authorizerId": authorizer} if authorizer else {}
    apigw.put_method(restApiId=api, resourceId=rid, httpMethod="GET", authorizationType=auth_type, **kw)
    apigw.put_integration(restApiId=api, resourceId=rid, httpMethod="GET", type="MOCK",
                          requestTemplates={"application/json": '{"statusCode": 200}'})
    apigw.put_method_response(restApiId=api, resourceId=rid, httpMethod="GET", statusCode="200")
    apigw.put_integration_response(restApiId=api, resourceId=rid, httpMethod="GET", statusCode="200",
                                   responseTemplates={"application/json": '{"msg":"hello"}'})


mock_method("open", "NONE")
mock_method("secure", "COGNITO_USER_POOLS", auth_id)
mock_method("iam", "AWS_IAM")
apigw.create_deployment(restApiId=api, stageName="dev")
base = f"http://floci:4566/restapis/{api}/dev/_user_request_"


def get(path, headers=None):
    return requests.get(base + path, headers=headers or {}, timeout=15).status_code


# ---------- E1 ----------
ck.check("E1.open(NONE).no-token", get("/open"), 200)
ck.check("E1.secure.no-token", get("/secure"), 401)
ck.check("E1.secure.garbage-token", get("/secure", {"Authorization": "abc.def.ghi"}), 401)
ck.check("E1.secure.token-from-other-pool", get("/secure", {"Authorization": other_tok["IdToken"]}), 401)
ck.check("E1.secure.IdToken", get("/secure", {"Authorization": tok["IdToken"]}), 200)


# ---------- E2 ----------
def signed_get(path, key, secret):
    req = AWSRequest(method="GET", url=base + path)
    SigV4Auth(Credentials(key, secret), "execute-api", "us-east-1").add_auth(req)
    return requests.get(base + path, headers=dict(req.headers), timeout=15).status_code


nobody = make_user("nobody")
ck.check("E2.iam.unsigned", get("/iam"), 403)
ck.check("E2.iam.signed-test-key", signed_get("/iam", "test", "test"), 200)
ck.check("E2.iam.signed-user-without-execute-api:Invoke(AWS: 403)", signed_get("/iam", nobody["key"], nobody["secret"]), 200, aws_diff=IAM,
         doc="api-gateway.md: Floci authenticates the caller but does not authorize the call")
ck.check("E2.iam.signed-wrong-secret", signed_get("/iam", nobody["key"], "WRONG"), 403)

ck.done()
