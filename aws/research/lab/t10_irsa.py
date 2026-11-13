"""T10 IRSA: EKS OIDC issuer -> AssumeRoleWithWebIdentity -> trust policy의 sub/aud 조건.

E1 같은 cluster 토큰: 맞는 service account / 다른 service account / 서명 변조 / aud 다름
E2 floci가 호스팅하지 않는 issuer의 토큰 (문서: enforcement off면 통과, on이면 InvalidIdentityToken)

EKS는 mock 모드(k3s 없이)로 띄우고, 토큰은 floci의 /_floci/eks/clusters/<name>/oidc-token 으로 받는다.
LAB_IAM=true|false 대조.
AWS 기대값: https://docs.aws.amazon.com/eks/latest/userguide/associate-service-account-role.html
           https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithWebIdentity.html
"""
import base64
import json
import os

import requests

from lib import Checker, c, outcome, policy

IAM = os.environ.get("LAB_IAM") == "true"
ck = Checker("t10")
eks, iam, sts = c("eks"), c("iam"), c("sts")
A = "000000000000"

role = iam.create_role(RoleName="eks-cluster", AssumeRolePolicyDocument=policy(
    {"Effect": "Allow", "Principal": {"Service": "eks.amazonaws.com"}, "Action": "sts:AssumeRole"}))["Role"]["Arn"]
eks.create_cluster(name="lab", roleArn=role, resourcesVpcConfig={})
issuer = eks.describe_cluster(name="lab")["cluster"]["identity"]["oidc"]["issuer"]
prov = issuer.replace("https://", "")
ck.info(f"issuer = {issuer}")
r, d = outcome(iam.create_open_id_connect_provider, Url=issuer, ClientIDList=["sts.amazonaws.com"], ThumbprintList=["a" * 40])
ck.info(f"CreateOpenIDConnectProvider = {r}")

iam.create_role(RoleName="irsa-reader", AssumeRolePolicyDocument=policy({
    "Effect": "Allow", "Principal": {"Federated": f"arn:aws:iam::{A}:oidc-provider/{prov}"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {"StringEquals": {f"{prov}:sub": "system:serviceaccount:app:reader", f"{prov}:aud": "sts.amazonaws.com"}}}))
RARN = f"arn:aws:iam::{A}:role/irsa-reader"


def mint(ns, sa, **kw):
    r = requests.post("http://floci:4566/_floci/eks/clusters/lab/oidc-token",
                      json={"namespace": ns, "serviceAccount": sa, **kw}, timeout=10)
    r.raise_for_status()
    return r.json()["token"]


def awiwi(token):
    return outcome(sts.assume_role_with_web_identity, RoleArn=RARN, RoleSessionName="pod", WebIdentityToken=token)


# ---------- E1 ----------
r, d = awiwi(mint("app", "reader"))
ck.check("E1.right-service-account", r, "ALLOW", d)
if r == "ALLOW":
    ck.info(f"SubjectFromWebIdentityToken = {d.get('SubjectFromWebIdentityToken')}")
r, d = awiwi(mint("app", "writer"))
ck.check("E1.other-service-account", r, "AccessDenied", d)
t = mint("app", "reader")
h, p, s = t.split(".")
s2 = ("A" if s[0] != "A" else "B") + s[1:]
r, d = awiwi(f"{h}.{p}.{s2}")
ck.check("E1.tampered-signature", r, "InvalidIdentityToken", d)
r, d = awiwi(mint("app", "reader", audience="something-else"))
ck.check("E1.wrong-audience", r, "InvalidIdentityToken", d)

# ---------- E2 ----------
def b64(o):
    return base64.urlsafe_b64encode(json.dumps(o).encode()).rstrip(b"=").decode()


foreign = f'{b64({"alg": "RS256", "typ": "JWT"})}.{b64({"iss": "https://issuer.example.com", "sub": "system:serviceaccount:app:reader", "aud": "sts.amazonaws.com", "exp": 4102444800})}.c2ln'
iam.create_role(RoleName="irsa-foreign", AssumeRolePolicyDocument=policy({
    "Effect": "Allow", "Principal": {"Federated": f"arn:aws:iam::{A}:oidc-provider/issuer.example.com"},
    "Action": "sts:AssumeRoleWithWebIdentity"}))
r, d = outcome(sts.assume_role_with_web_identity, RoleArn=f"arn:aws:iam::{A}:role/irsa-foreign",
               RoleSessionName="ext-pod", WebIdentityToken=foreign)
ck.check("E2.foreign-issuer-unsigned-token", r, "InvalidIdentityToken" if IAM else "ALLOW", d,
         doc="sts.md: tokens from an issuer Floci does not host are accepted unless IAM enforcement is on")

ck.done()
