# floci로 배울 수 있는 "AWS 고유의 것": 조사 결론

> 2026-11-12 이후 과목 방향은 서버리스 중심안으로 바뀌었다(사용자 승인 전): `curriculum-serverless.md`. 아래 7개 주제 중 권한 주제는 서버리스 단계의 연결 지점과 확장으로 옮겨 갔다. 이 문서의 실험 결과와 문서 대조는 그대로 유효하다. 단 STS "trust policy principal"의 AWS 동등성 판정은 정정이 필요하다(같은 계정 user를 trust에 직접 지정하면 AWS는 identity policy가 필요 없다. `curriculum-serverless.md` 함정 카드 마지막 줄).

## 결론

floci 2.4.0으로 확정할 수 있는 `aws/` 과목 주제는 아래 7개다. 모두 로컬 Docker 실험에서 on/off(또는 설정값) 대조로 기대 동작이 나왔고, 깨끗한 상태에서 두 번 돌려 같은 결과를 얻었다. 공통 조건은 IAM enforcement와 서명 검증 flag를 켜고, access key `test`가 아닌 IAM user나 role 세션으로 호출하는 것이다.

| # | 주제 | 한 줄 이유 | 레슨 | 문서 |
|---|---|---|---|---|
| 01 | IAM 정책 평가 순서 + SCP | 명시 Deny, permission boundary, session policy, SCP 상한이 모두 실제 거부 응답으로 재현됨 | 5 | `topics/01-iam-policy-evaluation.md` |
| 02 | STS AssumeRole과 trust policy | trust와 identity 양쪽 허용, ExternalId 없음/틀림/맞음이 각각 다른 응답으로 재현됨 | 3 | `topics/02-sts-assume-role-trust-policy.md` |
| 03 | IRSA (AssumeRoleWithWebIdentity) | EKS mock + floci OIDC 토큰으로 `sub`·`aud`·서명 검사가 단계별로 재현됨 | 2 | `topics/03-irsa-web-identity.md` |
| 04 | Resource policy와 공개 접근 (같은 계정) | 이름 지목 vs 계정 위임, 명시 Deny, 익명 접근과 Block Public Access가 재현됨. cross-account는 제외 | 3 | `topics/04-resource-policy-public-access.md` |
| 05 | Security Group | 이 PC(WSL2 Docker Desktop)에서 nftables로 실제 패킷을 거름. ingress·egress·SG source 규칙이 on/off로 갈림 | 3 | `topics/05-security-group.md` |
| 06 | Lambda 동시성·비동기 실패 처리·SQS ESM | 429, `approximateInvokeCount` 3 vs 1, VisibilityTimeout 뒤 DLQ 이동이 재현됨 | 3 | `topics/06-lambda-concurrency-async-esm.md` |
| 07 | Cognito → API Gateway authorizer, AWS_IAM 메서드 | 토큰 없음/무효/다른 pool 401, 정상 200이 재현됨. AWS_IAM은 인증까지만 | 2 | `topics/07-cognito-apigateway-authn.md` |

권장 순서: 01 → 02 → 04 → 03 → 07 → 05 → 06. 01·02·04는 같은 IAM 평가 엔진 위에 있고, 03·07은 "외부 신원을 AWS 권한으로 바꾸는 입구"이며, 05·06은 인가와 독립된 managed 동작이다. 합계 21레슨.

## 탈락 후보와 이유

| 후보 | 단계 | 이유 |
|---|---|---|
| SQS visibility timeout과 재시도 (단독) | 1단계 탈락 검사 | Redis Streams pending/XCLAIM, RabbitMQ로 같은 의미를 배울 수 있다(사용자가 redis·distsys에서 다룸). AWS 고유한 연결(Lambda ESM → RedrivePolicy)만 06 주제 E3에 넣었다 |
| EventBridge 패턴 매칭 | 1단계 탈락 검사 | JSON 필터 문법이라 mock으로도 같은 것을 배운다. 서비스 간 인가 쪽은 문서가 "Other target types store the role as configuration without assuming it or enforcing its IAM policies."(`eventbridge.md:304`)라 배울 수 없다 |
| envelope encryption (단독) | 1단계 탈락 검사 | data key로 암호화하는 절차는 아무 crypto 라이브러리로 된다. KMS 고유 부분(key policy, grant)만 실험했다 |
| VPC 라우팅·NACL·NAT·peering | 1단계 문서 + 2단계 실험 | 문서 원문 "This filters packets but does not emulate VPC routing, NACLs, NAT gateways, or peering."(`ec2.md:190`). deny-all NACL을 subnet에 붙여도 연결이 열려 있음을 실험으로 확인(`t05-*.log` E3) |
| KMS key policy와 grant | 2단계 실험 | IAM on에서 key policy의 명시 Deny도, account root를 뺀 key policy도 무시되고 Encrypt가 ALLOW. grant를 받은 user는 `AccessDeniedException`. AWS 고유 의미의 핵심 두 가지가 동작하지 않는다. encryption context 검사는 동작한다(`t07-*.log`) |
| CloudFormation 상태 머신과 rollback | 2단계 실험 후 보류 | 기본 rollback과 update rollback은 재현됨. `OnFailure=DO_NOTHING`이 무시되어 `ROLLBACK_COMPLETE`가 되고, 모르는 resource type은 stub으로 `CREATE_COMPLETE`. 인가·경계 중심인 이 과목의 우선순위가 낮아 확정 목록에서 뺐다. 필요하면 1~2레슨으로 붙일 수 있다(`t08-cfn.log`) |
| cross-account resource policy (SQS) | 2단계 실험 | 문서(`sqs.md:220`)와 반대로 동작한다. 아래 "문서와 다른 점" 3번 |

## 문서와 다른 점 (값 대조)

1. **AssumeRole `MaxSessionDuration`이 걸리지 않는다.** 문서 `sts.md:278`: "`AssumeRole` rejects a `DurationSeconds` above the role's `MaxSessionDuration` with `ValidationError` (400) … checked even when IAM policy enforcement is disabled." 실제: role `MaxSessionDuration=3600`, 요청 `DurationSeconds=7200` → off/on 모두 HTTP 200, 만료가 7200초 뒤. 43200 초과만 `ValidationError`.
2. **새 bucket의 기본 Block Public Access가 걸리지 않는다.** 문서 `s3.md:504`: "A bucket nobody configured enforces the default `GetPublicAccessBlock` reports for it: all four settings on." 실제: 같은 bucket의 `GetPublicAccessBlock`은 네 값 모두 `true`인데, `Principal:"*"` 읽기 bucket policy를 넣는 `PutBucketPolicy`가 성공한다. `PutPublicAccessBlock`을 명시적으로 호출한 bucket에서는 `AccessDenied`.
3. **SQS cross-account가 반대로 판정된다.** 문서 `sqs.md:220`: "A `QueueUrl` whose path names another account is a cross-account call: the queue's policy and the caller's identity policies both have to allow it." 실제(IAM on): 계정 `111111111111`의 `sqs:*` user가 queue policy 없이 계정 `000000000000`의 queue에 SendMessage 성공(메시지 1개가 A queue에 들어감). A queue ARN만 허용한 user는 queue policy가 이름으로 지목해도 `AccessDeniedException`. floci 로그: `IAM enforcement DENY: … action=sqs:SendMessage resource=arn:aws:sqs:us-east-1:111111111111:shared-q`. resource ARN의 계정을 queue 주인이 아니라 호출자로 만든다.
4. **SG enforcement를 켜면 보고된 private IP를 컨테이너가 갖지 않는다.** 문서 `ec2.md:1449`: "An instance's reported private IP is then an address its container actually holds". 실제(SG on): `DescribeInstances`는 `10.50.1.11`, 컨테이너 주소는 `172.17.0.2`, `172.30.0.4`. `10.50.1.11:8080`은 SG 규칙을 연 뒤에도 연결 실패, `172.30.0.4:8080`은 성공. SG off에서는 컨테이너가 `10.50.1.11`을 갖는다.

문서끼리 어긋난 곳 1건: 외부 issuer 토큰을 `eks.md:946`은 "accepted … requires no configuration flag"라고만 쓰고 `sts.md:327`은 enforcement on에서 `InvalidIdentityToken`이라고 쓴다. 실험은 `sts.md`와 같다.

floci 문서는 말하지 않지만 AWS와 다른 점: `OnFailure=DO_NOTHING` 무시(CloudFormation), KMS key policy 미평가, `CreateQueue VisibilityTimeout=99999` 허용(AWS 상한 43200, 실험 중 관찰, 스크립트에 고정 안 함).

## 남은 미확인

실험하지 않은 것:
- route table, NAT gateway, peering이 패킷에 영향 없는지 (문서 주장만)
- ECS `awsvpc` task의 SG 필터링, CIDR source SG 규칙, 호스트에서 들어오는 트래픽의 SG 판정
- EKS real 모드(k3s 컨테이너)에서 pod 안 projected token으로 IRSA 사용
- Lambda 함수 코드가 실행 role 자격증명으로 다른 서비스를 부를 때 enforcement가 걸리는지 (서비스 간 인가)
- Lambda function policy(`AddPermission`), SNS topic policy, EventBridge bus policy의 resource policy 평가
- EventBridge target `RoleArn` 미사용, API Gateway REST resource policy 미평가, CloudFormation `SetStackPolicy` 미강제 (문서 주장만)
- S3 cross-account (`FLOCI_SERVICES_S3_GLOBAL_BUCKET_NAMESPACE`)
- HTTP API(v2) JWT authorizer, Lambda authorizer, Cognito identity pool
- ESM `MaximumConcurrency` 미적용, S3 OnFailure destination 미전달 (문서 주장만)
- persistent storage 모드에서 같은 결과가 나오는지 (모든 실험은 기본 memory 모드)

읽지 않은 문서: `services/` 138개 중 이번 조사에서 한계 구간을 읽은 것은 `iam`, `sts`, `s3`, `sqs`, `lambda`, `ec2`, `kms`, `eventbridge`, `cloudformation`, `api-gateway`, `eks`, `cognito`, `organizations`의 관련 절과 `configuration/multi-account.md`, `environment-variables.md`, `docker.md`, `docker-images.md`, `docker-compose.md`다. 이전 가설본(`../floci-capability.md`)이 읽은 `elb`, `elb-classic`, `efs`, `route53`, `cloudfront`, `redshift`, `dynamodb`, `rds`, `ecs`(일부)를 합쳐도 약 115개는 `index.md` 한 줄만 봤다. 그중 후보 주제와 관련 있어 다음에 읽을 것:
`sns.md`(topic policy), `ecs.md`(awsvpc SG, task role), `step-functions.md`(Lambda task 인가), `ses.md`(서비스 principal 호출), `lambda-web-functions.md`, `cognitoidentity.md`(identity pool), `ram.md`(계정 간 공유), `access-analyzer.md`, `verifiedpermissions.md`, `ssoadmin.md`, `dsql.md`, `secrets-manager.md`(resource policy), `pipes.md`, `scheduler.md`(target role).

## 조사 환경

- 조사일: 2026-11-12
- floci: `floci/floci@sha256:5ee85db604c4aa74ac76e07ea5cc83086f37bb472bf3dbb97e34019e48efae9c`, 이미지 label `version=2.4.0`, `org.opencontainers.image.revision=9be236e2890c2042a6bb819f1a9228be996acd90`, 빌드 2026-10-31. compose(`lab/compose.yml`)에 digest로 고정했다. 문서(`aws/floci-docs/`)는 main 기준이라 이 버전과 어긋날 수 있다.
- 클라이언트: `lab/client/Dockerfile` (`python:3.12-slim` + `boto3==1.35.36`, `requests==2.32.3`), 이미지 이름 `awslab-client:boto3-1.35.36`. 호스트에는 AWS CLI·boto3를 설치하지 않았다.
- Docker: Docker Desktop, server 29.6.1, kernel `6.18.33.2-microsoft-standard-WSL2`, cgroup v2, SecurityOptions `seccomp`, `cgroupns` (rootless 아님).
- floci 컨테이너 설정: `FLOCI_RUN_AS_ROOT=true`, Docker socket mount, `FLOCI_SERVICES_DOCKER_NETWORK=awslab_default`, `FLOCI_SERVICES_EKS_MOCK=true`, `FLOCI_SERVICES_LAMBDA_ASYNC_RETRY_DELAY_SECONDS=0`. case마다 `LAB_IAM`, `LAB_SCP`, `LAB_SIG`, `LAB_S3AUTH`, `LAB_SG`로 flag를 바꾼다(`lab/cases.txt`).

## 재현성

- `lab/run.sh`: case마다 `docker compose down -v` → 지정 env로 up → 실험 → floci 로그 저장 → `down -v` → floci가 띄운 `floci-*` 컨테이너·볼륨·VPC 네트워크 삭제. 모든 case PASS면 종료 코드 0.
- `lab/verify.sh`: 전체 20개 case를 r1, r2 두 번 연속 돌리고 `CHECK`/`RESULT` 줄을 비교한다. 결과는 `lab/logs/r1/`, `lab/logs/r2/`, 비교는 `lab/logs/r1-vs-r2.diff`.
- 각 실험 스크립트는 기대값을 코드에 적고, 어긋나면 `MISMATCH`를 찍고 exit 1이다. 문서와 다르다고 확인한 항목은 관측값을 기대값으로 고정하고 `DOC-DIFF` 표시를 붙였다(회귀 감지용). floci 문서는 말이 없고 AWS와 다른 항목은 `AWS-DIFF`.
- 두 번 실행 결과(2026-11-12): r1, r2 모두 20개 case PASS(종료 코드 0), `CHECK`/`RESULT` 263줄이 r1과 r2에서 같다(`lab/logs/r1-vs-r2.diff` 0바이트). 그중 `DOC-DIFF` 8줄, `AWS-DIFF` 19줄. 콘솔 출력은 `lab/logs/verify-console.txt`.
- 실행마다 바뀌는 값: Docker 주소(SG 실험의 `172.30.0.x`), 계정 ID(Organizations `CreateAccount`), OIDC issuer id. 판정 줄에는 이 값을 넣지 않아 비교에 영향이 없다. 문서에 적은 주소는 r1의 값이다.
- 다시 돌리기: `cd aws/research/lab && ./verify.sh` (약 20분, Lambda 런타임과 alpine 이미지가 없으면 첫 실행에서 pull).

## 파일

```
aws/research/
├─ README.md               이 문서
├─ capability-matrix.md    기능별 문서 주장 / 실험 결과 / 판정 / 근거
├─ topics/01~07-*.md       확정 주제별 1쪽
└─ lab/
   ├─ compose.yml          floci(digest 고정) + boto3 client
   ├─ client/Dockerfile
   ├─ cases.txt            case 이름 | 스크립트 | env
   ├─ run.sh, verify.sh
   ├─ lib.py               client 생성, outcome(), Checker
   ├─ t01~t10_*.py, t05_sg.sh
   └─ logs/r1, logs/r2     case별 결과 로그(.log)와 floci 로그(.floci.log)
```
