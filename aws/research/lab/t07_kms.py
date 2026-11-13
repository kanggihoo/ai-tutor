"""T07 KMS key policy, grant, encryption context.

E1 key policy가 인가에 쓰이는가: key policy의 명시 Deny / account root를 빼 버린 key policy
E2 grant가 인가에 쓰이는가 (identity policy 없는 user에게 Encrypt grant)
E3 encryption context가 복호화 조건이 되는가 (envelope encryption의 data key)

LAB_IAM=true|false 대조.
AWS 기대값: https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html
           https://docs.aws.amazon.com/kms/latest/developerguide/grants.html
           https://docs.aws.amazon.com/kms/latest/developerguide/encrypt_context.html
"""
import os

from lib import Checker, allow, c, make_user, outcome, policy

IAM = os.environ.get("LAB_IAM") == "true"
ck = Checker("t07")
kms = c("kms")
A = "000000000000"
D = "AccessDeniedException"

eve = make_user("eve", policy(allow("kms:*")))
gus = make_user("gus")  # identity policy 없음

# ---------- E1 ----------
k1 = kms.create_key()["KeyMetadata"]["KeyId"]
kms.put_key_policy(KeyId=k1, PolicyName="default", Policy=policy(
    {"Effect": "Allow", "Principal": {"AWS": f"arn:aws:iam::{A}:root"}, "Action": "kms:*", "Resource": "*"},
    {"Effect": "Deny", "Principal": "*", "Action": "kms:Encrypt", "Resource": "*"}))
r, d = outcome(c("kms", **eve).encrypt, KeyId=k1, Plaintext=b"x")
ck.check("E1.key-policy-explicit-deny(AWS: AccessDenied)", r, "ALLOW", d, aws_diff=True,
         doc="iam.md Resource-based policies 목록(S3,SQS,SNS,Lambda,EventBridge,DSQL)에 KMS 없음 -> key policy 미평가로 읽힘")
k2 = kms.create_key()["KeyMetadata"]["KeyId"]
kms.put_key_policy(KeyId=k2, PolicyName="default", Policy=policy(
    {"Effect": "Allow", "Principal": {"AWS": f"arn:aws:iam::{A}:user/someone-else"}, "Action": "kms:*", "Resource": "*"}))
r, d = outcome(c("kms", **eve).encrypt, KeyId=k2, Plaintext=b"x")
ck.check("E1.key-policy-without-root(AWS: AccessDenied)", r, "ALLOW", d, aws_diff=True)
r, d = outcome(c("kms", **gus).encrypt, KeyId=k2, Plaintext=b"x")
ck.check("E1.no-identity-policy(gus)", r, D if IAM else "ALLOW", d, doc="identity policy는 KMS key ARN으로 평가(kms.md IAM Enforcement)")

# ---------- E2 ----------
k3 = kms.create_key()["KeyMetadata"]["KeyId"]
kms.create_grant(KeyId=k3, GranteePrincipal=f"arn:aws:iam::{A}:user/gus", Operations=["Encrypt", "Decrypt"])
ck.info(f"grants on k3 = {len(kms.list_grants(KeyId=k3)['Grants'])}")
r, d = outcome(c("kms", **gus).encrypt, KeyId=k3, Plaintext=b"x")
ck.check("E2.grant-to-gus.Encrypt(AWS: ALLOW)", r, D if IAM else "ALLOW", d, aws_diff=IAM,
         doc="kms.md Grant Support Scope: grants are not evaluated during crypto operations")

# ---------- E3 ----------
k4 = kms.create_key()["KeyMetadata"]["KeyId"]
dk = kms.generate_data_key(KeyId=k4, KeySpec="AES_256", EncryptionContext={"app": "orders"})
ck.check("E3.data-key.plaintext-32-bytes", len(dk["Plaintext"]), 32)
r, d = outcome(kms.decrypt, CiphertextBlob=dk["CiphertextBlob"], EncryptionContext={"app": "orders"})
ck.check("E3.decrypt-with-same-context", r == "ALLOW" and d["Plaintext"] == dk["Plaintext"], True)
r, d = outcome(kms.decrypt, CiphertextBlob=dk["CiphertextBlob"], EncryptionContext={"app": "billing"})
ck.check("E3.decrypt-with-other-context", r, "InvalidCiphertextException", d)
r, d = outcome(kms.decrypt, CiphertextBlob=dk["CiphertextBlob"])
ck.check("E3.decrypt-without-context", r, "InvalidCiphertextException", d)
kms.disable_key(KeyId=k4)
r, d = outcome(kms.decrypt, CiphertextBlob=dk["CiphertextBlob"], EncryptionContext={"app": "orders"})
ck.check("E3.decrypt-after-DisableKey", r, "DisabledException", d)

ck.done()
