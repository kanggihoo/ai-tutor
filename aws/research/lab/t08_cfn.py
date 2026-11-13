"""T08 CloudFormation stack 상태 머신과 rollback.

E1 create 실패: 기본(ROLLBACK) vs OnFailure=DO_NOTHING -> stack status와 먼저 만든 resource가 남는가
E2 update 실패: UPDATE_ROLLBACK_COMPLETE 와 이전 값 복원
E3 모르는 resource type (문서: stub 처리, AWS는 실패)

AWS 기대값: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-describing-stacks.html#w2ab1c23c15c17c11
           https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stack-failure-options.html
"""
import json
import time

from lib import Checker, c, outcome

ck = Checker("t08")
cfn, sqs = c("cloudformation"), c("sqs")


# 실패 유발: SQS DelaySeconds 5000 (허용 0~900). VisibilityTimeout 99999는 floci가 받아 줘서 쓰지 않는다
def tpl(p, good_vis=30, bad=True, fake=False):
    res = {"Good": {"Type": "AWS::SQS::Queue", "Properties": {"QueueName": f"{p}-good", "VisibilityTimeout": good_vis}}}
    if bad:
        res["Bad"] = {"Type": "AWS::SQS::Queue", "DependsOn": "Good",
                      "Properties": {"QueueName": f"{p}-bad", "DelaySeconds": 5000}}
    if fake:
        res["Fake"] = {"Type": "AWS::Fake::Thing", "Properties": {}}
    return json.dumps({"AWSTemplateFormatVersion": "2010-09-09", "Resources": res})


def settle(name, timeout=90):
    end = time.time() + timeout
    while time.time() < end:
        s = cfn.describe_stacks(StackName=name)["Stacks"][0]["StackStatus"]
        if not s.endswith("IN_PROGRESS"):
            return s
        time.sleep(1)
    return s


def queue_exists(name):
    return outcome(sqs.get_queue_url, QueueName=name)[0] == "ALLOW"


def reasons(name):
    ev = cfn.describe_stack_events(StackName=name)["StackEvents"]
    return [f'{e["LogicalResourceId"]}:{e["ResourceStatus"]}:{(e.get("ResourceStatusReason") or "")[:80]}' for e in ev][:8]


# ---------- E1 ----------
cfn.create_stack(StackName="s-rollback", TemplateBody=tpl("rb"))
st = settle("s-rollback")
ck.check("E1.default.status", st, "ROLLBACK_COMPLETE", reasons("s-rollback"))
ck.check("E1.default.good-queue-removed", queue_exists("rb-good"), False)
ck.info("events: " + " | ".join(reasons("s-rollback")))

cfn.create_stack(StackName="s-keep", TemplateBody=tpl("keep"), OnFailure="DO_NOTHING")
st = settle("s-keep")
# AWS: OnFailure=DO_NOTHING이면 CREATE_FAILED로 멈추고 만든 resource를 남긴다. floci 문서는 OnFailure를 언급하지 않는다
ck.check("E1.DO_NOTHING.status(AWS: CREATE_FAILED)", st, "ROLLBACK_COMPLETE", reasons("s-keep"), aws_diff=True,
         doc="cloudformation.md: OnFailure/DisableRollback 언급 없음")
ck.check("E1.DO_NOTHING.good-queue-kept(AWS: True)", queue_exists("keep-good"), False, aws_diff=True)

# ---------- E2 ----------
cfn.create_stack(StackName="s-upd", TemplateBody=tpl("upd", good_vis=30, bad=False))
ck.check("E2.create.status", settle("s-upd"), "CREATE_COMPLETE")
cfn.update_stack(StackName="s-upd", TemplateBody=tpl("upd", good_vis=60, bad=True))
st = settle("s-upd")
ck.check("E2.failed-update.status", st, "UPDATE_ROLLBACK_COMPLETE", reasons("s-upd"))
url = sqs.get_queue_url(QueueName="upd-good")["QueueUrl"]
vis = sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["VisibilityTimeout"])["Attributes"]["VisibilityTimeout"]
ck.check("E2.good-queue-VisibilityTimeout-restored", vis, "30")
ck.check("E2.bad-queue-absent", queue_exists("upd-bad"), False)
ck.info("events: " + " | ".join(reasons("s-upd")))

# ---------- E3 ----------
cfn.create_stack(StackName="s-fake", TemplateBody=tpl("fake", bad=False, fake=True))
st = settle("s-fake")
ck.check("E3.unknown-type.status(AWS: rollback)", st, "CREATE_COMPLETE", reasons("s-fake"), aws_diff=True,
         doc="cloudformation.md:257 Resource type AWS::Fake::Thing is not supported by Floci. It was stubbed and nothing was created for it.")
ck.info("events: " + " | ".join(reasons("s-fake")))

ck.done()
