"""T04 Organizations SCP.

E1 member 계정의 role session: SCP Deny s3:* 가 identity의 Allow * 를 덮는가
E2 member 계정 bare key(account root)도 SCP에 묶이는가, management 계정은 면제인가

LAB_SCP=true|false 대조 (LAB_IAM=true 고정).
AWS 기대값: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html
"""
import os
import time

from lib import Checker, allow, c, creds_of, deny, make_user, outcome, policy

SCP = os.environ.get("LAB_SCP") == "true"
ck = Checker("t04")
DENIED = ("AccessDenied", "AccessDeniedException")

org = c("organizations")
org.create_organization(FeatureSet="ALL")
st = org.create_account(Email="member@example.com", AccountName="member")["CreateAccountStatus"]
for _ in range(30):
    st = org.describe_create_account_status(CreateAccountRequestId=st["Id"])["CreateAccountStatus"]
    if st["State"] != "IN_PROGRESS":
        break
    time.sleep(1)
M = st["AccountId"]
ck.info(f"member account = {M} state={st['State']}")
root_id = org.list_roots()["Roots"][0]["Id"]
org.enable_policy_type(RootId=root_id, PolicyType="SERVICE_CONTROL_POLICY")
pid = org.create_policy(Name="deny-s3", Description="x", Type="SERVICE_CONTROL_POLICY",
                        Content=policy(deny("s3:*")))["Policy"]["PolicySummary"]["Id"]
org.attach_policy(PolicyId=pid, TargetId=M)

# management(000000000000)의 admin user가 member의 OrganizationAccountAccessRole을 assume
admin = make_user("admin", policy(allow("*")))
r, d = outcome(c("iam", key=M, secret="x").get_role, RoleName="OrganizationAccountAccessRole")
ck.info(f"OrganizationAccountAccessRole exists in member: {r}")
r, d = outcome(c("sts", **admin).assume_role, RoleArn=f"arn:aws:iam::{M}:role/OrganizationAccountAccessRole",
               RoleSessionName="lab-org")
ck.check("E1.assume-OrganizationAccountAccessRole", r, "ALLOW", d)
sess = creds_of(d["Credentials"]) if r == "ALLOW" else None

# ---------- E1 ----------
if sess:
    ck.info(f"session = {c('sts', **sess).get_caller_identity()['Arn']}")
    r, d = outcome(c("s3", **sess).list_buckets)
    ck.check("E1.member-session.s3:ListAllMyBuckets(SCP deny s3:*)", r, DENIED if SCP else "ALLOW", d)
    r, d = outcome(c("sqs", **sess).list_queues)
    ck.check("E1.member-session.sqs:ListQueues(not in SCP deny)", r, "ALLOW", d)

# ---------- E2 ----------
r, d = outcome(c("s3", key=M, secret="x").list_buckets)
ck.check("E2.member-bare-key(account root).s3", r, DENIED if SCP else "ALLOW", d,
         doc="iam.md: account-root principal is subject to SCPs")
org.attach_policy(PolicyId=pid, TargetId=root_id)  # root에도 붙여도 management는 면제
r, d = outcome(c("s3", **admin).list_buckets)
ck.check("E2.management-account-user.s3(exempt)", r, "ALLOW", d)
r, d = outcome(c("s3").list_buckets)
ck.check("E2.test-key.s3(never SCP-denied)", r, "ALLOW", d)

ck.done()
