"""T03 resource policy와 cross-account.

E1 S3 bucket policy (같은 계정): 이름으로 지목된 principal / 계정만 지목(위임) / 명시 Deny
E2 SQS queue policy (다른 계정 111111111111의 user가 000000000000의 queue에 SendMessage)
E3 익명 S3 GET: IAM enforcement와 S3 ENFORCE_AUTH의 관계

LAB_IAM, LAB_S3AUTH 대조.
AWS 기대값: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic-cross-account.html
           https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html#principal-accounts
"""
import json
import os

import requests

from lib import Checker, allow, c, make_user, outcome, policy

IAM = os.environ.get("LAB_IAM") == "true"
S3AUTH = os.environ.get("LAB_S3AUTH") == "true"
ck = Checker("t03")
A, B = "000000000000", "111111111111"
DENIED = ("AccessDenied", "AccessDeniedException")

# ---------- E1 ----------
s3 = c("s3")
s3.create_bucket(Bucket="rp-bucket")
s3.put_object(Bucket="rp-bucket", Key="k", Body=b"hello")
dave = make_user("dave")                      # identity 없음, bucket policy가 이름으로 지목
erin = make_user("erin")                      # identity 없음, bucket policy는 계정 root만 지목
frank = make_user("frank", policy(allow("s3:*")))  # identity 허용, bucket policy가 명시 Deny
s3.put_bucket_policy(Bucket="rp-bucket", Policy=policy(
    {"Effect": "Allow", "Principal": {"AWS": f"arn:aws:iam::{A}:user/dave"}, "Action": "s3:GetObject", "Resource": "arn:aws:s3:::rp-bucket/*"},
    {"Effect": "Allow", "Principal": {"AWS": f"arn:aws:iam::{A}:root"}, "Action": "s3:GetObject", "Resource": "arn:aws:s3:::rp-bucket/*"},
    {"Effect": "Deny", "Principal": {"AWS": f"arn:aws:iam::{A}:user/frank"}, "Action": "s3:GetObject", "Resource": "arn:aws:s3:::rp-bucket/*"},
))
r, d = outcome(c("s3", **dave).get_object, Bucket="rp-bucket", Key="k")
ck.check("E1.dave(named in bucket policy, no identity)", r, "ALLOW", d)
r, d = outcome(c("s3", **erin).get_object, Bucket="rp-bucket", Key="k")
# IAM: 계정만 지목 = 위임 -> identity 없으니 거부. S3AUTH만: 소유 계정 principal은 기본 허용(s3.md Evaluation Rules 3)
ck.check("E1.erin(account-root only, no identity)", r, "AccessDenied" if IAM else "ALLOW", d)
r, d = outcome(c("s3", **frank).get_object, Bucket="rp-bucket", Key="k")
ck.check("E1.frank(identity allow + bucket deny)", r, "AccessDenied" if (IAM or S3AUTH) else "ALLOW", d)

# ---------- E2 ----------
# 문서(sqs.md "Queue policies under IAM enforcement"): QueueUrl이 다른 계정을 가리키면 cross-account.
#   queue policy와 caller identity policy가 둘 다 허용해야 한다.
# 실제: IAM filter가 resource ARN을 caller 계정(111111111111)으로 만든다(floci 로그
#   "action=sqs:SendMessage resource=arn:aws:sqs:us-east-1:111111111111:shared-q").
#   그래서 identity에 A의 queue ARN을 적으면 거부, sqs:* 이면 queue policy 없이도 A의 queue에 들어간다.
sqs_a = c("sqs")
qurl = sqs_a.create_queue(QueueName="shared-q")["QueueUrl"]
qarn = f"arn:aws:sqs:us-east-1:{A}:shared-q"
iam_b = c("iam", key=B, secret="x")  # 12자리 bare key = 계정 B root (SCP 없으면 enforcement 우회)
bee = make_user("bee", policy(allow("sqs:SendMessage", qarn)), iam=iam_b)   # identity: A queue ARN만
beeall = make_user("beeall", policy(allow("sqs:*")), iam=iam_b)             # identity: sqs:* (Resource *)
ck.info(f"bee caller = {c('sts', **bee).get_caller_identity()['Arn']}")
r, d = outcome(c("sqs", **beeall).send_message, QueueUrl=qurl, MessageBody="beeall-no-policy")
ck.check("E2.B.beeall(sqs:*)->A.queue(no queue policy)", r, "ALLOW", d,
         doc="cross-account needs queue policy too -> AWS: AccessDenied", doc_diff=IAM)
r, d = outcome(c("sqs", **bee).send_message, QueueUrl=qurl, MessageBody="bee-no-policy")
ck.check("E2.B.bee(A-queue-ARN)->A.queue(no queue policy)", r, DENIED if IAM else "ALLOW", d)
sqs_a.set_queue_attributes(QueueUrl=qurl, Attributes={"Policy": policy(
    {"Effect": "Allow", "Principal": {"AWS": f"arn:aws:iam::{B}:user/bee"},
     "Action": "sqs:SendMessage", "Resource": qarn})})
r, d = outcome(c("sqs", **bee).send_message, QueueUrl=qurl, MessageBody="bee-with-policy")
ck.check("E2.B.bee(A-queue-ARN)->A.queue(queue policy names bee)", r, DENIED if IAM else "ALLOW", d,
         doc="identity + queue policy both allow -> AWS: ALLOW", doc_diff=IAM)
n = int(sqs_a.get_queue_attributes(QueueUrl=qurl, AttributeNames=["ApproximateNumberOfMessages"])["Attributes"]["ApproximateNumberOfMessages"])
ck.check("E2.messages-landed-in-A-queue", n, 1 if IAM else 3)
r, d = outcome(c("sqs", key=B, secret="x").list_queues)
ck.check("E2.queues-in-B(count)", len((d.get("QueueUrls") if r == "ALLOW" else None) or []), 0)

# ---------- E3 ----------
s3.create_bucket(Bucket="anon-bucket")
s3.put_object(Bucket="anon-bucket", Key="obj", Body=b"public?")
url = "http://floci:4566/anon-bucket/obj"
st = requests.get(url, timeout=10).status_code
ck.check("E3.anonymous-GET(private bucket)", st, 403 if S3AUTH else 200, aws_diff=not S3AUTH,
         doc="iam.md: REST requests are not checked (IAM filter). s3.md: ENFORCE_AUTH decides anonymous")
s3.delete_public_access_block(Bucket="anon-bucket")
s3.put_bucket_policy(Bucket="anon-bucket", Policy=policy(
    {"Effect": "Allow", "Principal": "*", "Action": "s3:GetObject", "Resource": "arn:aws:s3:::anon-bucket/*"}))
st = requests.get(url, timeout=10).status_code
ck.check("E3.anonymous-GET(public-read policy)", st, 200)
# BlockPublicPolicy는 flag와 무관하게 거부 (s3.md Block Public Access 표)
s3.create_bucket(Bucket="bpa-bucket")
pab = s3.get_public_access_block(Bucket="bpa-bucket")["PublicAccessBlockConfiguration"]
ck.check("E3.fresh-bucket.GetPublicAccessBlock(all four true)", all(pab.values()), True)
pub = lambda b: policy({"Effect": "Allow", "Principal": "*", "Action": "s3:GetObject", "Resource": f"arn:aws:s3:::{b}/*"})
r, d = outcome(s3.put_bucket_policy, Bucket="bpa-bucket", Policy=pub("bpa-bucket"))
ck.check("E3.fresh-bucket.public-policy(default BPA)", r, "ALLOW", d,
         doc="s3.md: a bucket nobody configured enforces the default ... all four settings on -> AccessDenied",
         doc_diff=True)
s3.create_bucket(Bucket="bpa-explicit")
s3.put_public_access_block(Bucket="bpa-explicit", PublicAccessBlockConfiguration={
    "BlockPublicAcls": True, "IgnorePublicAcls": True, "BlockPublicPolicy": True, "RestrictPublicBuckets": True})
r, d = outcome(s3.put_bucket_policy, Bucket="bpa-explicit", Policy=pub("bpa-explicit"))
ck.check("E3.explicit-PutPublicAccessBlock.public-policy", r, "AccessDenied", d)

ck.done()
