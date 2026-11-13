#!/usr/bin/env bash
# T05 Security Group enforcement (LAB_SG=true|false 대조). run.sh가 호스트에서 실행한다.
# E1 ingress: B의 SG에 규칙이 없을 때 / sg-client를 source로 8080을 열었을 때
# E2 egress: A의 기본 egress를 지웠을 때 / B SG로 가는 8080 egress만 열었을 때
# E3 NACL: subnet에 deny-all NACL을 붙여도 통신이 되는가 (문서: NACL은 에뮬레이션하지 않음)
# 그리고 DescribeInstances의 PrivateIpAddress로 실제 접속이 되는가
# AWS 기대값: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html
#            https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html
set -u
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")"
mkdir -p logs/tmp
SG="${LAB_SG:-false}"
MODE="${LAB_MODE:-}"
fail=0
api() { docker compose --profile client run --rm -T -e LAB_MODE="$MODE" client python /lab/t05_api.py "$@" < /dev/null 2>/dev/null; }
check() { # name expected actual [doc] [docdiff]
  if [ "$2" = "$3" ]; then t=OK; else t=MISMATCH; fail=$((fail+1)); fi
  [ "${5:-}" = docdiff ] && t="$t DOC-DIFF"
  [ "${5:-}" = awsdiff ] && t="$t AWS-DIFF"
  echo "CHECK t05[$MODE] $1 expected=$2 actual=$3 $t${4:+ | doc: $4}"
}
echo "=== t05 MODE=$MODE"
st=$(api setup); echo "INFO  setup $st"
A=floci-aws-${LAB_NS:-awslab}-ec2-$(echo "$st" | python -c 'import sys,json;print(json.load(sys.stdin)["a"])')
B=floci-aws-${LAB_NS:-awslab}-ec2-$(echo "$st" | python -c 'import sys,json;print(json.load(sys.stdin)["b"])')
B_REPORTED=$(echo "$st" | python -c 'import sys,json;print(json.load(sys.stdin)["b_ip"])')
# B가 실제로 가진 주소들 (lo 제외)
B_ADDRS=$(docker exec "$B" sh -c "ip -4 -o addr | awk '\$2!=\"lo\"{print \$4}' | cut -d/ -f1" | tr '\n' ' ')
echo "INFO  B reported PrivateIpAddress=$B_REPORTED, B container addrs=[$B_ADDRS]"
echo "INFO  A privileged=$(docker inspect "$A" --format '{{.HostConfig.Privileged}}') netmode=$(docker inspect "$A" --format '{{.HostConfig.NetworkMode}}' | cut -c1-20)"
docker exec -d "$B" sh -c 'while true; do echo hi-from-b | nc -l -p 8080; done'
sleep 1
probe() { # $1=ip -> OPEN / BLOCKED
  out=$(docker exec "$A" sh -c "timeout 4 nc $1 8080 </dev/null" 2>/dev/null)
  case "$out" in *hi-from-b*) echo OPEN;; *) echo BLOCKED;; esac
}
# 시험에 쓸 B 주소: reported IP가 B에 실제로 있으면 그것, 없으면 floci 네트워크(awslab_default) 쪽 주소
if echo " $B_ADDRS " | grep -q " $B_REPORTED "; then HELD=yes; TARGET=$B_REPORTED; else HELD=no
  TARGET=$(docker inspect "$B" --format '{{range $k,$v := .NetworkSettings.Networks}}{{if eq $k "awslab_default"}}{{$v.IPAddress}}{{end}}{{end}}')
  [ -z "$TARGET" ] && TARGET=$(docker exec "$B" sh -c "ip -4 -o addr show eth1 | awk '{print \$4}' | cut -d/ -f1")
fi
echo "INFO  probe target=$TARGET (reported IP held by container: $HELD)"
if [ "$SG" = true ]; then exp_held=no; else exp_held=yes; fi
check "E0.reported-private-ip-held-by-container" "$exp_held" "$HELD" "ec2.md VPC Docker networks: reported private IP is an address its container actually holds" "$([ "$SG" = true ] && echo docdiff)"
check "E0.reported-private-ip-reachable" "$([ "$SG" = true ] && echo BLOCKED || echo OPEN)" "$( [ "$HELD" = yes ] && echo OPEN || probe "$B_REPORTED")"

# ---------- E1 ----------
if [ "$SG" = true ]; then e=BLOCKED; else e=OPEN; fi
check "E1.no-ingress-rule.A->B:8080" "$e" "$(probe "$TARGET")" "" "$([ "$SG" = true ] || echo awsdiff)"
api allow-a-to-b >/dev/null; sleep 2
check "E1.ingress-from-sg-client.A->B:8080" OPEN "$(probe "$TARGET")"
# ---------- E2 ----------
api revoke-a-egress >/dev/null; sleep 2
check "E2.A-egress-revoked.A->B:8080" "$e" "$(probe "$TARGET")" "" "$([ "$SG" = true ] || echo awsdiff)"
api allow-a-egress-8080 >/dev/null; sleep 2
check "E2.A-egress-8080-to-sg-server.A->B:8080" OPEN "$(probe "$TARGET")"
# ---------- E3 ----------
echo "INFO  nacl $(api nacl-deny-all)"; sleep 2
check "E3.deny-all-NACL-on-subnet.A->B:8080(AWS would block)" OPEN "$(probe "$TARGET")" "ec2.md: does not emulate VPC routing, NACLs, NAT gateways, or peering" awsdiff
if [ "$SG" = true ]; then
  docker exec "${B/ec2/sg}" sh -c 'nft list table inet floci_sg' 2>/dev/null | sed 's/^/INFO  nft(B): /' | head -14
fi
echo "RESULT t05[$MODE] $([ $fail -eq 0 ] && echo PASS || echo FAIL) mismatches=$fail"
exit $fail
