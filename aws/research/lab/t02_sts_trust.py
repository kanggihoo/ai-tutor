"""T02 STS AssumeRole과 trust policy.

E1 trust policy principal + caller identity policy 둘 다 필요한가
E2 sts:ExternalId (confused deputy 방지)
E3 문서가 적은 한계: 세션 태그 조건, MFA 조건, MaxSessionDuration

LAB_IAM=true|false 대조.
AWS 기대값: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user_externalid.html
           https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic-cross-account.html
"""
import os

from lib import Checker, allow, c, make_user, outcome, policy

IAM = os.environ.get("LAB_IAM") == "true"
ck = Checker("t02")
iam = c("iam")
ACCT = "000000000000"
D = "AccessDenied"

alice = make_user("alice", policy(allow("sts:AssumeRole"), allow("sts:TagSession")))
bob = make_user("bob", policy(allow("sts:AssumeRole")))
carol = make_user("carol")  # identity policy 없음

def role(name, trust, **kw):
    iam.create_role(RoleName=name, AssumeRolePolicyDocument=trust, **kw)
    iam.put_role_policy(RoleName=name, PolicyName="p", PolicyDocument=policy(allow("s3:ListAllMyBuckets")))
    return f"arn:aws:iam::{ACCT}:role/{name}"

def assume(who, arn, **kw):
    return outcome(c("sts", **who).assume_role, RoleArn=arn, RoleSessionName="lab-session", **kw)

# ---------- E1 ----------
app = role("app-role", policy({"Effect": "Allow", "Action": "sts:AssumeRole", "Principal": {"AWS": [
    f"arn:aws:iam::{ACCT}:user/alice", f"arn:aws:iam::{ACCT}:user/carol"]}}))
r, d = assume(alice, app)
ck.check("E1.alice(in trust, identity allows)", r, "ALLOW", d)
r, d = assume(bob, app)
ck.check("E1.bob(not in trust, identity allows)", r, D if IAM else "ALLOW", d)
r, d = assume(carol, app)
ck.check("E1.carol(in trust, no identity allow)", r, D if IAM else "ALLOW", d)
r, d = assume(alice, f"arn:aws:iam::{ACCT}:role/no-such-role")
ck.check("E1.alice->nonexistent-role", r, D, d, doc="sts.md: target role must exist (enforcement 무관)")

# ---------- E2 ----------
ext = role("vendor-role", policy({"Effect": "Allow", "Action": "sts:AssumeRole",
                                  "Principal": {"AWS": f"arn:aws:iam::{ACCT}:root"},
                                  "Condition": {"StringEquals": {"sts:ExternalId": "ext-123"}}}))
r, d = assume(alice, ext)
ck.check("E2.no-external-id", r, D if IAM else "ALLOW", d)
r, d = assume(alice, ext, ExternalId="wrong")
ck.check("E2.wrong-external-id", r, D if IAM else "ALLOW", d)
r, d = assume(alice, ext, ExternalId="ext-123")
ck.check("E2.right-external-id", r, "ALLOW", d)

# ---------- E3 ----------
tagged = role("tag-role", policy({"Effect": "Allow", "Action": ["sts:AssumeRole", "sts:TagSession"],
                                  "Principal": {"AWS": f"arn:aws:iam::{ACCT}:root"},
                                  "Condition": {"StringEquals": {"aws:RequestTag/team": "red"}}}))
r, d = assume(alice, tagged, Tags=[{"Key": "team", "Value": "red"}])
# AWS라면 ALLOW. 문서: aws:RequestTag는 context에 없어 조건이 맞지 않는다
ck.check("E3.session-tag-condition(AWS would ALLOW)", r, D if IAM else "ALLOW", d, aws_diff=IAM,
         doc="sts.md Known limitations: aws:RequestTag/* not in request context")

mfa_user = make_user("mfa-user", policy(allow("s3:ListAllMyBuckets",
                                              Condition={"Bool": {"aws:MultiFactorAuthPresent": "true"}})))
r, d = outcome(c("s3", **mfa_user).list_buckets)
ck.check("E3.mfa-gated-allow(never grants)", r, D if IAM else "ALLOW", d, aws_diff=IAM,
         doc="iam.md: Allow gated on aws:MultiFactorAuthPresent never grants")

short = role("short-role", policy({"Effect": "Allow", "Action": "sts:AssumeRole",
                                   "Principal": {"AWS": f"arn:aws:iam::{ACCT}:root"}}), MaxSessionDuration=3600)
r, d = assume(alice, short, DurationSeconds=7200)
# 문서: ValidationError(400). 실제: 200, Expiration이 7200초 뒤로 나온다
ck.check("E3.duration-above-max(7200>MaxSessionDuration 3600)", r, "ALLOW", d if r != "ALLOW" else None,
         doc="sts.md Trust Policy Enforcement: rejects DurationSeconds above MaxSessionDuration with ValidationError (400)",
         doc_diff=True)
if r == "ALLOW":
    import datetime
    left = (d["Credentials"]["Expiration"] - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
    ck.check("E3.duration-above-max.issued-lifetime>3600s", left > 3700, True)
r, d = assume(alice, short, DurationSeconds=50000)
ck.check("E3.duration-above-43200(API hard limit)", r, "ValidationError", d)
r, d = assume(alice, short, DurationSeconds=3600)
ck.check("E3.duration-equal-max", r, "ALLOW", d)

ck.done()
