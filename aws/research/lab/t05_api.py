"""T05 Security Group 실험의 API 단계. t05_sg.sh가 단계별로 부른다.
상태는 /lab/logs/tmp/t05.json 에 둔다.
"""
import json
import sys
import time

from lib import c

ST = "/lab/logs/tmp/t05.json"
ec2 = c("ec2")
cmd = sys.argv[1]


def load():
    return json.load(open(ST))


def save(s):
    json.dump(s, open(ST, "w"))


if cmd == "setup":
    vpc = ec2.create_vpc(CidrBlock="10.50.0.0/16")["Vpc"]["VpcId"]
    sub = ec2.create_subnet(VpcId=vpc, CidrBlock="10.50.1.0/24")["Subnet"]["SubnetId"]
    sga = ec2.create_security_group(GroupName="sg-client", Description="client", VpcId=vpc)["GroupId"]
    sgb = ec2.create_security_group(GroupName="sg-server", Description="server, no ingress", VpcId=vpc)["GroupId"]

    def run(sg):
        return ec2.run_instances(ImageId="ami-alpine", InstanceType="t3.micro", MinCount=1, MaxCount=1,
                                 SubnetId=sub, SecurityGroupIds=[sg])["Instances"][0]["InstanceId"]

    a, b = run(sga), run(sgb)
    for _ in range(120):
        ins = {i["InstanceId"]: i for r in ec2.describe_instances(InstanceIds=[a, b])["Reservations"] for i in r["Instances"]}
        if all(ins[x]["State"]["Name"] == "running" for x in (a, b)):
            break
        time.sleep(2)
    s = dict(vpc=vpc, sub=sub, sga=sga, sgb=sgb, a=a, b=b,
             a_ip=ins[a].get("PrivateIpAddress"), b_ip=ins[b].get("PrivateIpAddress"))
    save(s)
    print(json.dumps(s))

elif cmd == "allow-a-to-b":  # B의 ingress에 "sg-client에서 오는 tcp 8080" 허용
    s = load()
    ec2.authorize_security_group_ingress(GroupId=s["sgb"], IpPermissions=[{
        "IpProtocol": "tcp", "FromPort": 8080, "ToPort": 8080, "UserIdGroupPairs": [{"GroupId": s["sga"]}]}])
    print("ok")

elif cmd == "revoke-a-egress":  # A의 기본 egress(-1, 0.0.0.0/0) 제거
    s = load()
    ec2.revoke_security_group_egress(GroupId=s["sga"], IpPermissions=[{
        "IpProtocol": "-1", "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}])
    print("ok")

elif cmd == "allow-a-egress-8080":
    s = load()
    ec2.authorize_security_group_egress(GroupId=s["sga"], IpPermissions=[{
        "IpProtocol": "tcp", "FromPort": 8080, "ToPort": 8080, "UserIdGroupPairs": [{"GroupId": s["sgb"]}]}])
    print("ok")

elif cmd == "nacl-deny-all":  # subnet에 inbound/outbound 모두 deny 하는 NACL을 붙인다
    s = load()
    acl = ec2.create_network_acl(VpcId=s["vpc"])["NetworkAcl"]["NetworkAclId"]
    for egress in (False, True):
        ec2.create_network_acl_entry(NetworkAclId=acl, RuleNumber=1, Protocol="-1", RuleAction="deny",
                                     Egress=egress, CidrBlock="0.0.0.0/0")
    assoc = [a for n in ec2.describe_network_acls(Filters=[{"Name": "vpc-id", "Values": [s["vpc"]]}])["NetworkAcls"]
             for a in n.get("Associations", []) if a["SubnetId"] == s["sub"]]
    ec2.replace_network_acl_association(AssociationId=assoc[0]["NetworkAclAssociationId"], NetworkAclId=acl)
    now = [a["NetworkAclId"] for n in ec2.describe_network_acls(NetworkAclIds=[acl])["NetworkAcls"]
           for a in n.get("Associations", []) if a["SubnetId"] == s["sub"]]
    print(json.dumps({"acl": acl, "associated": now}))
