# 05. Security Group: stateful 방화벽, SG를 source로 쓰는 규칙, egress

## ① 배울 것
Security Group이 인스턴스 단위 stateful 방화벽이라는 것, 규칙의 source에 CIDR 대신 다른 SG를 쓸 수 있다는 것, ingress와 egress가 각각 따로 막는다는 것을 실제 TCP 연결 성공/실패로 확인한다.

## ② 왜 MinIO·PostgreSQL 등으로 안 되는가
iptables나 Docker network로도 패킷 필터링은 연습할 수 있다. 이 주제가 AWS에 고유한 부분은 "IP가 아니라 SG 멤버십을 source로 쓰는 규칙"과 "규칙이 ENI에 붙고 응답 트래픽은 자동 허용(stateful)"이라는 모델이다. 일반 Docker에는 SG 개념이 없어 같은 규칙을 직접 IP로 풀어 써야 한다.

## ③ floci 검증 결과와 판정
실험: `lab/t05_sg.sh` + `lab/t05_api.py` (case `t05-off`, `t05-sg`). 환경: Docker Desktop 29.6.1, WSL2 kernel `6.18.33.2-microsoft-standard-WSL2`, rootless 아님. 인스턴스 A(`sg-client`), B(`sg-server`, ingress 없음), 둘 다 `ami-alpine`. B에서 `nc -l -p 8080`, A에서 `nc <B> 8080`. 기대값 출처: [Security groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html), [Network ACLs](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html).

| 확인한 것 | SG enforcement off | SG enforcement on | 판정 |
|---|---|---|---|
| B의 SG에 ingress 규칙 없음 → A→B:8080 | OPEN | BLOCKED | 실험 확인 (on/off 대조) |
| B ingress에 "source = sg-client, tcp 8080" 추가 | OPEN | OPEN | 실험 확인 |
| A의 기본 egress(`-1`, `0.0.0.0/0`) 삭제 | OPEN | BLOCKED | 실험 확인 |
| A egress에 "dest = sg-server, tcp 8080"만 추가 | OPEN | OPEN | 실험 확인 |
| subnet에 inbound/outbound deny-all NACL 연결 | OPEN | OPEN (AWS라면 막힘) | 실험 확인 (`ec2.md:190` "does not emulate VPC routing, NACLs, NAT gateways, or peering") |
| `DescribeInstances`의 B `PrivateIpAddress`(10.50.1.11)를 컨테이너가 실제로 갖는가 | 예 (`10.50.1.11` 보유) | **아니오** (`172.17.0.x`, `172.30.0.x`만 보유) | **문서와 다름** (on에서) |

SG on일 때 B 쪽 nftables 규칙(규칙 추가 후, floci가 만든 `floci-aws-sg-<instance>` 컨테이너 안, `lab/logs/r1/t05-sg.log`에서 발췌. Docker 주소는 실행마다 바뀐다):
```
table inet floci_sg {
	chain ingress {
		type filter hook input priority filter - 10; policy drop;
		iifname "lo" accept
		ct state established,related accept
		...
		ip saddr 172.30.0.5 tcp dport 8080 accept
		ip saddr 172.30.0.5 drop
```
`sg-client`라는 SG 이름이 A의 Docker 주소(`172.30.0.5`)로 풀려 들어가 있다. `ct state established,related accept`가 stateful 동작의 근거다.

문서와 다른 항목의 값 대조:

| | 문서 (`ec2.md:1449`) | 실제 (SG on) |
|---|---|---|
| reported private IP | "An instance's reported private IP is then an address its container actually holds, drawn from the subnet CIDR the caller declared" | `DescribeInstances`는 `10.50.1.11`을 보고하지만 B 컨테이너 주소는 `172.17.0.2`, `172.30.0.4`. A에서 `10.50.1.11:8080`으로는 규칙을 연 뒤에도 연결 실패, `172.30.0.4:8080`으로는 성공 |

## ④ floci에서 깨지거나 주의가 필요한 부분
- SG를 켜면 실습에서 `DescribeInstances`의 private IP 대신 컨테이너의 Docker 주소로 접속해야 한다. 레슨 스크립트가 `docker inspect`로 주소를 찾아 준다(`t05_sg.sh` 38~42줄).
- SG를 끄면 모든 규칙이 무시되고 전부 OPEN이다. 대조 없이 "열렸다"를 보면 SG 효과로 착각한다.
- NACL, route table, NAT gateway, peering은 API로 만들어지지만 패킷에 영향이 없다. "서브넷이 인터넷과 어떻게 이어지는가"는 이 환경에서 배울 수 없다.
- CIDR source 규칙(`10.0.0.0/8` 같은)과 호스트에서 들어오는 트래픽은 시험하지 않았다(확인 못 함). Docker Desktop은 외부 클라이언트 주소를 바꿀 수 있다고 문서에 적혀 있다(`ec2.md:192`).
- ECS `awsvpc` task의 SG 필터링은 시험하지 않았다(확인 못 함).

## ⑤ 실습 스크립트
- `aws/research/lab/t05_sg.sh`, `aws/research/lab/t05_api.py` — 실행: `./run.sh t05`

## ⑥ 예상 레슨 수와 순서 (3)
1. ingress 없음 → 막힘, SG를 source로 열기 → 열림 (off와 나란히 보여 줘 enforcement 효과 확인)
2. egress도 막는다, stateful이라 응답은 규칙 없이 돌아온다 (nft 규칙의 `ct state established`)
3. NACL은 여기서 효과가 없다는 것을 직접 보고, 실제 AWS의 NACL(stateless, 번호 순)과 차이를 말로 정리
