"""T01 IAM 정책 평가 순서.

E1 identity allow / implicit deny / `test` key 우회 / 모르는 key
E2 explicit Deny > Allow, permission boundary, session policy
E3 서비스별 enforcement 범위(정책 없는 user로 읽기 호출 14개) + 위조 secret

LAB_IAM=true|false, LAB_SIG=true|false 로 대조한다.
AWS 기대값: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html
"""
import os

DENIED = ("AccessDenied", "AccessDeniedException", "AuthorizationError")
from lib import Checker, allow, c, creds_of, deny, make_user, outcome, policy

IAM = os.environ.get("LAB_IAM") == "true"
SIG = os.environ.get("LAB_SIG") == "true"
ck = Checker("t01")
iam = c("iam")

# ---------- E1 ----------
alice = make_user("alice", policy(allow("s3:ListAllMyBuckets")))
r, d = outcome(c("s3", **alice).list_buckets)
ck.check("E1.alice.s3:ListAllMyBuckets(allowed by identity)", r, "ALLOW", d)
r, d = outcome(c("sqs", **alice).list_queues)
ck.check("E1.alice.sqs:ListQueues(no allow -> implicit deny)", r, DENIED if IAM else "ALLOW", d)
r, d = outcome(c("sqs").list_queues)
ck.check("E1.test-key.sqs:ListQueues(bypass)", r, "ALLOW", d)
r, d = outcome(c("sqs", key="AKIAEXAMPLEUNKNOWN01", secret="x").list_queues)
ck.check("E1.unknown-AKIA.sqs:ListQueues", r, ("InvalidClientTokenId", "UnrecognizedClientException") if (IAM or SIG) else "ALLOW", d)

# ---------- E2 ----------
# explicit deny
a2 = make_user("alice2", policy(allow("s3:*"), deny("s3:CreateBucket")))
r, d = outcome(c("s3", **a2).create_bucket, Bucket="e2-deny-wins")
ck.check("E2.explicit-deny-beats-allow.s3:CreateBucket", r, DENIED if IAM else "ALLOW", d)
r, d = outcome(c("s3", **a2).list_buckets)
ck.check("E2.same-user-other-action.s3:ListAllMyBuckets", r, "ALLOW", d)

# permission boundary: identity는 *, boundary는 sqs:* 만
b_arn = iam.create_policy(PolicyName="boundary-sqs-only", PolicyDocument=policy(allow("sqs:*")))["Policy"]["Arn"]
bob = make_user("bob", policy(allow("*")), boundary_arn=b_arn)
r, d = outcome(c("s3", **bob).list_buckets)
ck.check("E2.boundary-caps.s3:ListAllMyBuckets", r, DENIED if IAM else "ALLOW", d)
r, d = outcome(c("sqs", **bob).list_queues)
ck.check("E2.boundary-allows.sqs:ListQueues", r, "ALLOW", d)

# session policy: role은 *, AssumeRole 때 s3:ListAllMyBuckets만 넘김
iam.create_role(RoleName="admin-role", AssumeRolePolicyDocument=policy(
    {"Effect": "Allow", "Principal": {"AWS": "arn:aws:iam::000000000000:root"}, "Action": "sts:AssumeRole"}))
iam.put_role_policy(RoleName="admin-role", PolicyName="all", PolicyDocument=policy(allow("*")))
carol = make_user("carol", policy(allow("sts:AssumeRole")))
cr = c("sts", **carol).assume_role(RoleArn="arn:aws:iam::000000000000:role/admin-role", RoleSessionName="sess1",
                                   Policy=policy(allow("s3:ListAllMyBuckets")))["Credentials"]
r, d = outcome(c("s3", **creds_of(cr)).list_buckets)
ck.check("E2.session-policy-allows.s3:ListAllMyBuckets", r, "ALLOW", d)
r, d = outcome(c("sqs", **creds_of(cr)).list_queues)
ck.check("E2.session-policy-caps.sqs:ListQueues", r, DENIED if IAM else "ALLOW", d)
cr2 = c("sts", **carol).assume_role(RoleArn="arn:aws:iam::000000000000:role/admin-role", RoleSessionName="sess2")["Credentials"]
r, d = outcome(c("sqs", **creds_of(cr2)).list_queues)
ck.check("E2.no-session-policy.sqs:ListQueues", r, "ALLOW", d)

# ---------- E3 ----------
nobody = make_user("nobody")
calls = {
    "s3:ListAllMyBuckets": lambda k: c("s3", **k).list_buckets(),
    "sqs:ListQueues": lambda k: c("sqs", **k).list_queues(),
    "sns:ListTopics": lambda k: c("sns", **k).list_topics(),
    "dynamodb:ListTables": lambda k: c("dynamodb", **k).list_tables(),
    "lambda:ListFunctions": lambda k: c("lambda", **k).list_functions(),
    "kms:ListKeys": lambda k: c("kms", **k).list_keys(),
    "secretsmanager:ListSecrets": lambda k: c("secretsmanager", **k).list_secrets(),
    "ssm:DescribeParameters": lambda k: c("ssm", **k).describe_parameters(),
    "ec2:DescribeVpcs": lambda k: c("ec2", **k).describe_vpcs(),
    "iam:ListUsers": lambda k: c("iam", **k).list_users(),
    "events:ListRules": lambda k: c("events", **k).list_rules(),
    "logs:DescribeLogGroups": lambda k: c("logs", **k).describe_log_groups(),
    "cloudformation:ListStacks": lambda k: c("cloudformation", **k).list_stacks(),
    "states:ListStateMachines": lambda k: c("stepfunctions", **k).list_state_machines(),
}
for name, fn in calls.items():
    r, d = outcome(fn, nobody)
    ck.check(f"E3.coverage.{name}", r, DENIED if IAM else "ALLOW", d)
r, d = outcome(c("sts", **nobody).get_caller_identity)
ck.check("E3.coverage.sts:GetCallerIdentity(no policy needed)", r, "ALLOW", d)

# 위조 secret: alice의 AKID + 엉뚱한 secret
forged = dict(key=alice["key"], secret="WRONG-SECRET-xxxxxxxxxxxxxxxxxxxxxxxxxxxx")
r, d = outcome(c("s3", **forged).list_buckets)
ck.check("E3.forged-secret.s3:ListAllMyBuckets", r, "SignatureDoesNotMatch" if SIG else "ALLOW", d, aws_diff=not SIG,
         doc="validate-signatures 꺼져 있으면 AKID만 본다(multi-account.md)")
r, d = outcome(c("sqs", **forged).list_queues)
exp = ("SignatureDoesNotMatch", "InvalidSignatureException") if SIG else (DENIED if IAM else "ALLOW")
ck.check("E3.forged-secret.sqs:ListQueues(alice has no sqs allow)", r, exp, d)

ck.done()
