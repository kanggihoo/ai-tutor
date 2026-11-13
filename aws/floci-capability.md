> 문서 기반 가설본, 실험결과는 `research/capability-matrix.md`

# floci로 어디까지 가능한가 (services 문서 기준)

출처는 `aws/floci-docs/`의 GitHub 원본 markdown이다. 문서에 적힌 내용만 정리했고, 실제로 floci를 띄워 확인한 것은 하나도 없다. 아래 표의 "확인"은 "문서에 그렇게 적혀 있다"는 뜻이다. 문서를 읽지 않은 부분은 "미확인"으로 따로 적었다.

읽은 범위: `services/index.md`(서비스 표 전체), `ec2.md`, `s3.md`, `lambda.md`, `sts.md`, `elb.md`, `elb-classic.md`, `efs.md`, `route53.md`, `cloudfront.md`, `eks.md`, `api-gateway.md`, `redshift.md`, `dynamodb.md`, `rds.md`(일부), `ecs.md`(일부), `kms.md`(일부), `cloudformation.md`(일부), `iam.md`(앞서 읽은 내용). 나머지 약 115개 서비스는 `index.md`의 한 줄(엔드포인트, 프로토콜, operation 수)만 봤다.

## 1. 전체 규모

서비스 문서는 138페이지(overview 1 + 서비스 137)이고, 표에는 약 150개 행이 있다. 모두 포트 `4566` 하나로 받으며 실제 AWS wire protocol을 쓴다. `AWS_ENDPOINT_URL=http://localhost:4566`와 access key `test`만 주면 AWS CLI와 SDK가 그대로 붙는다.

operation 수가 큰 서비스는 IAM 180, EC2 225, Glue 135, RDS 117, SES v2 102, Cognito 91, Service Catalog 89, API Gateway v1 85, SSO Admin 79이다.

## 2. 구현 깊이로 나눈 세 부류

### A. 실제 프로세스나 컨테이너가 뜨는 서비스 (Docker socket 필요)

| 서비스 | 실제로 뜨는 것 |
|---|---|
| Lambda | 함수마다 Docker 컨테이너. `arm64`/`x86_64`는 `HONOUR_ARCHITECTURES=true`일 때만 따른다 |
| EC2 | 인스턴스마다 Docker 컨테이너 (`tail -f /dev/null`, 카탈로그에 따라 systemd) |
| ECS | task가 Docker 컨테이너. `awsvpc` task는 ENI를 받는다 |
| EKS | 클러스터마다 k3s 컨테이너, API 서버가 호스트 포트 6500대에 열린다. IRSA용 OIDC issuer도 floci가 호스팅 |
| RDS | PostgreSQL, MySQL, MariaDB, SQL Server 컨테이너 + TCP proxy. IAM 인증 토큰 검증 포함 |
| ElastiCache, MemoryDB | RESP(Redis) proxy |
| OpenSearch, MSK(Redpanda), Amazon MQ(RabbitMQ), DocumentDB(mongo), Redshift(PostgreSQL), Timestream InfluxDB, ECR(`registry:2`) | 각 엔진 컨테이너 |

### B. 컨테이너 없이 floci가 직접 의미를 구현한 서비스

S3(58 operation), SQS, SNS, DynamoDB, Kinesis, EventBridge, Step Functions, KMS, Secrets Manager, Cognito(OAuth·JWKS 포함), CloudFormation(36 action + 수십 개 resource type), API Gateway v1/v2(실제 proxy 실행 포함), CloudWatch Logs·Metrics, SES, IAM, STS, Organizations 등.

### C. control plane만 있거나 stub인 서비스

| 서비스 | 문서에 적힌 한계 |
|---|---|
| EFS | "Metadata Only". NFS data plane이 없어 mount해서 읽고 쓰면 실패한다. lifecycle policy는 저장만 한다 |
| ELB Classic | listener 포트를 기록할 뿐 socket을 열지 않고 트래픽도 전달하지 않는다 |
| QuickSight | "metadata only" |
| Bedrock Runtime | stub. streaming은 `501` |
| Bedrock AgentCore data plane | canned response stub |
| CloudFront | `TestFunction`은 저장만 하고 실행하지 않는다. 전역 CDN 전파와 영속 edge cache 없음. S3 origin으로 POST·PUT 등을 보내면 403 |
| Route 53 | public authoritative 쪽은 TXT, NS, SOA 외 record type과 routing policy 없음. DNSSEC, traffic policy 없음 |
| EC2 네트워킹 일부 | 아래 3절 |

미확인: Budgets, Cost Explorer, Pricing, CUR, GuardDuty, Macie, Textract, Rekognition 등은 `stub`, `canned` 같은 단어가 문서에 나오지만 어느 정도인지 읽지 않았다.

## 3. 학습 주제별 판정

앞서 정한 학습 후보(IAM 평가, VPC 네트워킹, managed service 의미, 비용 모델)를 기준으로 했다.

### IAM 평가: 가능 (기본값은 꺼져 있음)

- `FLOCI_SERVICES_IAM_ENFORCEMENT_ENABLED=true`로 켠다. 기본값은 `false`이고, 꺼져 있으면 정책을 만들 수는 있어도 요청을 막지 않는다.
- 평가 순서는 SCP, explicit Deny, identity Allow, session policy, permission boundary, implicit deny다. SCP는 `FLOCI_SERVICES_ORGANIZATIONS_SCP_ENFORCEMENT_ENABLED`도 켜야 한다.
- access key `test`는 항상 통과한다. IAM 평가를 보려면 `test`가 아닌 key를 써야 한다. 모르는 key는 403이다.
- resource policy 평가는 S3, SQS, SNS, Lambda, EventBridge, DSQL에서 한다. S3 Control 경로도 IAM action으로 인가한다.
- 한계(문서 확인):
  - 세션 태그, `aws:RequestTag/*`, `sts:SourceIdentity`는 요청 컨텍스트에 없어서 이에 대한 Condition은 맞지 않는다. `sts:TagSession`도 검사하지 않는다 (`sts.md`).
  - MFA condition key는 채워지지 않는다.
  - API Gateway REST API resource policy는 저장만 하고 평가하지 않는다. KMS grant는 생성·조회는 되지만 암호화 연산의 인가에 쓰이지 않는다 (`kms.md`).
  - CloudFormation `SetStackPolicy`도 구조만 검사하고 강제하지 않는다.
  - `Simulate*`는 `EvalDecision`만 돌려준다.
  - 매핑할 수 없는 action은 허용한다.
- 미확인: S3 `FLOCI_SERVICES_S3_ENFORCE_AUTH`와 IAM enforcement가 서로 어떻게 맞물리는지, 이 변수 하나로 어느 서비스까지 인가가 걸리는지(서비스별 전수 확인 안 함).

### VPC 네트워킹: 거의 불가 (Security Group만 부분 가능)

- 문서 원문: Security Group enforcement는 "packets를 거를 뿐 VPC routing, NACL, NAT gateway, peering은 에뮬레이션하지 않는다".
- `FLOCI_NETWORK_SECURITY_GROUP_ENFORCEMENT_ENABLED=true`일 때만 nftables로 SG ingress·egress를 건다. 꺼져 있으면 같은 Docker network 안의 컨테이너끼리 모든 포트로 통한다.
- Route Table, NACL, NAT Gateway, VPC Peering은 API로 만들고 조회할 수 있고(`ec2.md`에 "local EC2 store"에 저장한다고 적혀 있음), 위 원문대로 패킷 경로에는 반영되지 않는다. Transit Gateway도 API는 있으나 트래픽 반영 여부는 문서에서 확인 못 함. NAT Gateway는 zonal만 지원하고 regional은 `UnsupportedOperation`이다.
- VPC 한 개가 Docker network 한 개다. VPC 사이 격리는 Docker daemon의 `DOCKER-ISOLATION` 규칙에 기대며, OrbStack에서는 적용되지 않는다고 적혀 있다.
- 사용자 환경 관련: 문서에 `Rootless Docker and Windows containers are unsupported`라고 되어 있다. 이 PC의 `docker info`는 `OSType=linux`, 커널 `...microsoft-standard-WSL2`, SecurityOptions에 rootless 없음이라 두 경우 모두 해당하지 않는다. 다만 SG enforcement가 Docker Desktop의 WSL2 VM에서 실제로 동작하는지(nftables, network namespace)는 띄워 보기 전에는 확인 못 함. Windows와 macOS의 Docker Desktop에서는 컨테이너 IP로 호스트에서 직접 접속할 수 없다는 점도 문서에 있다.
- 결론: "서브넷이 인터넷과 어떻게 이어지는가"(IGW, NAT, 라우팅, NACL 순서)는 floci로 연습할 수 없다. 실제 AWS 계정이 필요하다.

### managed service 의미: 서비스마다 갈림

- 잘 되는 쪽: RDS는 실제 엔진이라 SQL 동작과 IAM 인증 토큰이 진짜다. Lambda는 실제 컨테이너 실행, reserved concurrency 429 같은 의미까지 구현했다. SQS, SNS, DynamoDB, EventBridge, Step Functions는 API 의미를 직접 구현했다.
- 얕은 쪽:
  - Redshift는 클러스터 노드 수와 상관없이 컨테이너 1개이고 DB 이름은 `dev`로 고정된다.
  - DynamoDB는 Limits 항목에 replica 미지원, `TableId` 없음이 있다. DynamoDB Local 기반 제약인지 조건은 확인 못 함.
  - EKS는 cluster/nodegroup 업데이트, add-on, access policy가 미구현이다.
  - Auto Scaling은 실제 EC2 컨테이너를 늘리고 줄이는 reconciler가 있지만 일부 시나리오는 미구현이다.
  - Lambda `InvokeWithResponseStream`, layer permission, code signing 강제는 없다.
  - S3 Metadata, `CreateSession`은 `501`이다. ECS는 placement constraint를 평가하지 않는다.
- 실제 AWS의 failover, Multi-AZ, 용량 제한, 쿼터, 지연 같은 "운영 중 거동"은 문서상 대상이 아니다. 예를 들어 RDS `OptionGroupQuotaExceededFault`는 "에뮬레이터에 쿼터를 걸면 테스트에 방해만 된다"며 강제하지 않는다.

### 비용 모델: 불가

Budgets, Cost Explorer, Pricing, CUR, BCM Pricing Calculator가 서비스 표에 있다. 이 서비스들이 실제 청구액을 계산해 주지는 않으며(floci에는 청구가 없다), 응답 내용은 읽지 않았다. 비용 구조 학습은 AWS 공식 요금 문서와 실제 계정의 Budget 알림으로 해야 한다.

## 4. IaC와 배포 쪽

- CloudFormation은 resource type 대부분을 처리하지만 모르는 type은 `Resource type AWS::Fake::Thing is not supported by Floci. It was stubbed and nothing was created for it.`처럼 stub 처리한다. Redshift cluster, Redshift Serverless namespace 등은 CloudFormation에서 지원하지 않는다고 적혀 있다.
- Terraform(AWS provider)과 AWS CDK가 붙는다는 언급이 문서 곳곳에 있다(`terraform`, `CDK::Metadata`). 실제로 `terraform apply`가 끝까지 되는지는 확인 못 함.
- CodeBuild, CodeDeploy, CodePipeline, CodeArtifact, ECR이 있어 CI/CD 흐름의 API 모양은 연습할 수 있다. 실제 build 실행 범위는 읽지 않았다.

## 5. 결론

| 목적 | floci로 가능한가 |
|---|---|
| SDK/CLI로 S3, SQS, SNS, DynamoDB, Lambda, EventBridge, Step Functions 호출 | 가능 (B 부류, 서비스 대부분이 의미까지 구현) |
| IAM 정책 평가, trust policy, assume role, SCP | 가능하나 enforcement를 켜야 하고 `test` key는 우회됨. 세션 태그·MFA 조건은 안 됨 |
| 컨테이너 앱(ECS, EKS) 배포 흐름 | 가능 (실제 Docker/k3s). 단 ECS placement constraint는 평가하지 않고, EKS는 cluster·nodegroup 업데이트와 add-on이 미구현 |
| RDS, ElastiCache 등 DB 연결 | 가능 (실제 엔진) |
| VPC 라우팅, NACL, NAT, Peering, Transit Gateway | 불가 (API 레코드만) |
| Security Group | Linux Docker에서 enforcement 옵션을 켜면 가능 |
| EFS 마운트, Classic ELB 트래픽, CloudFront 전역 배포 | 불가 |
| 비용, 쿼터, 장애·failover 거동 | 불가 |

따라서 floci 한 가지로 AWS를 "배운다"고 하기에는 IAM과 managed service API 호출까지가 범위이고, VPC 네트워킹과 비용 모델은 실제 AWS 계정과 소액 Budget이 필요하다.
