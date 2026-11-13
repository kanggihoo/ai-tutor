# floci 2.4.0 기능별 검증표

조사일 2026-11-12. 이미지 `floci/floci@sha256:5ee85db604c4aa74ac76e07ea5cc83086f37bb472bf3dbb97e34019e48efae9c` (`org.opencontainers.image.version=2.4.0`, revision `9be236e2890c2042a6bb819f1a9228be996acd90`). 문서는 `aws/floci-docs/`(main 기준 원본)이고 줄 번호는 그 파일 기준이다.

## 판정 기준

- **기대값**: floci 문서가 그 동작을 말하면 문서 주장, 말하지 않으면 AWS 공식 문서의 동작(URL은 각 `lab/t*.py` 머리 주석과 `topics/`에 있다).
- **실험 확인**: 실험 결과가 기대값과 같다.
- **문서와 다름**: floci 문서의 주장과 실험 결과가 다르다. 두 값을 나란히 적는다.
- **AWS와 다름(문서 언급 없음)**: floci 문서가 말하지 않는 동작에서 실험 결과가 AWS 문서의 동작과 다르다. 이것을 "문서와 다름"으로 쓰면 floci 문서가 틀렸다고 말하는 셈이라 따로 둔다.
- **확인 못 함**: 실험하지 않았다. 문서 주장만 있다.
- "AWS와 같은가" 열은 판정과 별개다. "실험 확인"이어도 floci가 한계라고 밝힌 동작이면 "다름"이다.
- on/off 대조가 가능한 항목은 두 설정으로 각각 돌렸다. 근거의 로그는 `lab/logs/r1/<case>.log`이고, `lab/logs/r2/`에 같은 결과가 다시 있다(README "재현성" 절).

## IAM / STS / Organizations

| 서비스·기능 | 문서 주장 | 실험 결과 | 판정 | AWS와 같은가 | 근거 |
|---|---|---|---|---|---|
| IAM enforcement 기본값 | 기본 꺼짐, `FLOCI_SERVICES_IAM_ENFORCEMENT_ENABLED=true`로 켬 (`iam.md:1779`, `:1794`) | off: 정책 없는 user가 14개 서비스 모두 ALLOW / on: 14개 모두 거부 | 실험 확인 | 켜면 같음 | `t01-off.log`, `t01-iam.log` E3.coverage |
| enforcement 적용 서비스 범위 | resource ARN을 floci가 만드는 서비스 목록 (`iam.md:1820`~) | S3, SQS, SNS, DynamoDB, Lambda, KMS, Secrets Manager, SSM, EC2, IAM, EventBridge, Logs, CloudFormation, Step Functions 14개 읽기 호출이 정책 없을 때 거부됨. 거부 코드: S3·EC2·IAM·CloudFormation `AccessDenied`, SNS `AuthorizationError`, 나머지 `AccessDeniedException` | 실험 확인 | 같음 | `t01-iam.log` |
| access key `test` | 항상 허용, 정책 조회 없음 (`iam.md:2482`) | on에서도 `sqs:ListQueues` ALLOW | 실험 확인 | 다름(로컬 전용 우회) | `t01-iam.log` E1 |
| 존재하지 않는 `AKIA…` key | on에서 403 거부 (`iam.md` Bypass rules) | off: ALLOW / on: `UnrecognizedClientException` | 실험 확인 | 같음 | `t01-*.log` E1 |
| 명시 Deny > Allow | 평가 순서 2 (`iam.md:1808`) | on: `s3:CreateBucket` `AccessDenied`, 같은 user `ListAllMyBuckets` ALLOW | 실험 확인 | 같음 | `t01-iam.log` E2 |
| permission boundary | 평가 순서 5 (`iam.md:1811`) | on: identity `*` + boundary `sqs:*` → S3 거부, SQS 허용 | 실험 확인 | 같음 | `t01-iam.log` E2 |
| session policy | 평가 순서 4 (`iam.md:1810`) | on: session policy 밖 SQS 거부, session policy 없는 세션은 허용 | 실험 확인 | 같음 | `t01-iam.log` E2 |
| `sts:GetCallerIdentity` | 정책 평가 없음 (`iam.md` Bypass rules) | 정책 없는 user도 ALLOW | 실험 확인 | 같음 | `t01-iam.log` E3 |
| 서명 검증 (S3 외) | 기본은 검증 안 함, AKID만 봄 (`multi-account.md:31`, `:172`) | IAM on + SIG off: 위조 secret으로 S3 ALLOW, SQS는 정책대로 `AccessDeniedException` / SIG on: S3 `SignatureDoesNotMatch`, SQS `InvalidSignatureException` | 실험 확인 | SIG off는 다름 | `t01-iam.log`, `t01-iam-sig.log` E3.forged-secret |
| trust policy principal | on에서 trust 평가, caller identity도 `sts:AssumeRole` 허용 필요 (`sts.md:283`~) | on: trust 밖 `bob` 거부, identity 없는 `carol` 거부 / off: 둘 다 ALLOW | 실험 확인 | 같음 | `t02-*.log` E1 |
| 없는 role assume | 403 (`sts.md:275`) | off/on 모두 `AccessDenied` | 실험 확인 | 같음 | `t02-*.log` E1 |
| `sts:ExternalId` 조건 | 없거나 다르면 거부 (`sts.md` Trust Policy Enforcement) | on: 없음·`wrong` 거부, `ext-123` 허용 / off: 모두 허용 | 실험 확인 | 같음 | `t02-*.log` E2 |
| `MaxSessionDuration` | "`AssumeRole` rejects a `DurationSeconds` above the role's `MaxSessionDuration` with `ValidationError` (400) … checked even when IAM policy enforcement is disabled." (`sts.md:278`) | role 3600, 요청 7200 → off/on 모두 HTTP 200, 만료 +7200초 | **문서와 다름** | 다름 | `t02-*.log` E3.duration-above-max |
| `DurationSeconds` > 43200 | (API 상한) | `ValidationError` "Member must have value less than or equal to 43200" | 실험 확인 | 같음 | `t02-*.log` E3 |
| 세션 태그 조건 | `aws:RequestTag/*` 미모델, 조건 불일치 (`sts.md:309`) | on: `Tags=[team=red]` + 조건 `aws:RequestTag/team=red` → `AccessDenied` | 실험 확인 | 다름 | `t02-iam.log` E3 |
| MFA 조건 | MFA 키를 context에 넣지 않음, MFA 조건 Allow는 절대 허용 안 됨 (`iam.md:1084`) | on: `Bool aws:MultiFactorAuthPresent=true` Allow → `AccessDenied` | 실험 확인 | 다름 | `t02-iam.log` E3 |
| SCP 상한 | IAM + SCP 두 flag 필요, 계층 모두 허용해야 함 (`iam.md` SCPs) | SCP on: member session S3 `AccessDenied`, SQS ALLOW / SCP off: S3 ALLOW | 실험 확인 | 같음 | `t04-*.log` E1 |
| `OrganizationAccountAccessRole` | (Organizations `CreateAccount`) | member 계정에 role이 생기고 management user가 assume 가능 | 실험 확인 | 같음 | `t04-*.log` INFO |
| account root(bare 12자리 key)와 SCP | SCP 상한이 있으면 account root도 묶임 (`iam.md` "The account-root principal is subject to SCPs") | SCP on: `AccessDenied` / off: ALLOW | 실험 확인 | 같음 | `t04-*.log` E2 |
| management 계정 면제 | "management account is exempt" (`iam.md:2460`) | root에 Deny SCP를 붙여도 management user S3 ALLOW | 실험 확인 | 같음 | `t04-iam-scp.log` E2 |
| `test` key와 SCP | "never SCP-denied" (`iam.md:2461`) | ALLOW | 실험 확인 | 다름(로컬 전용) | `t04-iam-scp.log` E2 |

## Resource policy / S3

| 서비스·기능 | 문서 주장 | 실험 결과 | 판정 | AWS와 같은가 | 근거 |
|---|---|---|---|---|---|
| bucket policy가 user를 지목 | 같은 계정에서 지목된 principal은 identity 없이 허용 (`iam.md` Resource-based policies, `s3.md` Evaluation Rules) | `dave` off/IAM/S3AUTH 모두 ALLOW | 실험 확인 | 같음 | `t03-*.log` E1 |
| 계정 root만 지목 = 위임 | 같은 계정에서는 그 자체로 아무것도 주지 않음 (`iam.md` Resource-based policies) | IAM on: `erin` `AccessDenied` | 실험 확인 | 같음 | `t03-iam.log` E1 |
| S3 ENFORCE_AUTH만 켰을 때 소유 계정 principal | "For bucket owners … default decision is **Allow** unless explicitly denied." (`s3.md:461`) | `erin` ALLOW, `frank`(명시 Deny) `AccessDenied` | 실험 확인 | 다름(IAM 평가 없이 소유 계정 전체 허용) | `t03-s3auth.log` E1 |
| bucket policy 명시 Deny | Deny가 이김 | IAM on, S3AUTH on 모두 `frank` `AccessDenied` | 실험 확인 | 같음 | `t03-*.log` E1 |
| 익명 S3 GET, IAM만 on | "**REST requests are not checked.** … including an unsigned S3 call." (`iam.md:3070`) | 비공개 bucket 익명 GET 200 | 실험 확인 | 다름 | `t03-iam.log` E3 |
| 익명 S3 GET, ENFORCE_AUTH on | 공개 policy/ACL 없으면 거부 (`s3.md` Signature Verification 표) | 비공개 403, public-read policy 뒤 200 | 실험 확인 | 같음 | `t03-s3auth.log` E3 |
| 새 bucket의 Block Public Access | "A bucket nobody configured enforces the default `GetPublicAccessBlock` reports for it: all four settings on." (`s3.md:504`) | `GetPublicAccessBlock` 네 값 true인데 public bucket policy `PutBucketPolicy` 성공 (off/IAM/S3AUTH 모두) | **문서와 다름** | 다름 | `t03-*.log` E3.fresh-bucket |
| 명시 `PutPublicAccessBlock` 뒤 public policy | 403 (`s3.md:502`) | `AccessDenied` | 실험 확인 | 같음 | `t03-*.log` E3 |
| SQS cross-account queue policy | "A `QueueUrl` whose path names another account is a cross-account call: the queue's policy and the caller's identity policies both have to allow it." (`sqs.md:220`) | IAM on: B의 `sqs:*` user가 queue policy 없이 A queue에 SendMessage ALLOW(메시지 A queue에 1개). A queue ARN만 허용한 user는 queue policy가 지목해도 `AccessDeniedException`. floci 로그 `resource=arn:aws:sqs:us-east-1:111111111111:shared-q` | **문서와 다름** | 다름 | `t03-iam.log` E2, `t03-iam.floci.log` |
| SQS cross-account, enforcement off | (multi-account: QueueUrl 경로로 계정 결정) | B의 user 3번 SendMessage 모두 A queue에 들어감, B에는 queue 0개 | 실험 확인 | 다름(인가 없음) | `t03-off.log` E2 |

## EC2 / VPC

| 서비스·기능 | 문서 주장 | 실험 결과 | 판정 | AWS와 같은가 | 근거 |
|---|---|---|---|---|---|
| SG enforcement on WSL2 Docker Desktop | rootful Linux Docker + nftables 필요 (`environment-variables.md:107`), rootless·Windows container 미지원 (`ec2.md:190`) | 인스턴스마다 `floci-aws-sg-<id>` 컨테이너와 `table inet floci_sg`(policy drop) 생성, 실제로 패킷을 거름 | 실험 확인 | — | `t05-sg.log` INFO nft |
| SG ingress | on에서만 필터 (`ec2.md:190`) | 규칙 없음: off OPEN / on BLOCKED. source=sg-client 8080 추가 뒤 on OPEN | 실험 확인 | on은 같음 | `t05-*.log` E1 |
| SG egress | sender egress도 검사 (`ec2.md:190`) | 기본 egress 삭제: off OPEN / on BLOCKED. dest=sg-server 8080 추가 뒤 OPEN | 실험 확인 | on은 같음 | `t05-*.log` E2 |
| stateful 응답 | "Established replies use connection tracking." (`ec2.md:190`) | nft 규칙 `ct state established,related accept`, 응답 문자열 수신 | 실험 확인 | 같음 | `t05-sg.log` |
| NACL | 에뮬레이션 안 함 (`ec2.md:190`) | subnet에 deny-all NACL 연결(associate 확인) 뒤에도 OPEN (off/on) | 실험 확인 | 다름 | `t05-*.log` E3 |
| reported private IP | "An instance's reported private IP is then an address its container actually holds" (`ec2.md:1449`) | SG off: B가 `10.50.1.11` 보유, 그 주소로 OPEN / SG on: `DescribeInstances`는 `10.50.1.11`, 컨테이너는 `172.17.0.2`, `172.30.0.4`만 보유, `10.50.1.11:8080`은 규칙과 무관하게 연결 실패 | **문서와 다름** (SG on일 때) | 다름 | `t05-sg.log` E0, INFO |
| route table / NAT / peering | 에뮬레이션 안 함 (`ec2.md:190`) | 실험하지 않음 | 확인 못 함 | — | — |
| ECS `awsvpc` task SG | SG on이면 task namespace 필터 (`ecs.md:889`) | 실험하지 않음 | 확인 못 함 | — | — |

## Lambda

| 서비스·기능 | 문서 주장 | 실험 결과 | 판정 | AWS와 같은가 | 근거 |
|---|---|---|---|---|---|
| reserved concurrency | 초과 호출은 `TooManyRequestsException` 429 (`lambda.md:413`) | 예약 1, 동시 3 → ALLOW 1 / 429 2. 예약 없음 → ALLOW 3. 예약 0 → 429 | 실험 확인 | 같음 | `t06-lambda.log` E1 |
| unreserved 최소 100 | `PutFunctionConcurrency`가 100을 남겨야 함 (`lambda.md` Concurrency enforcement) | 950 예약 → `LimitExceededException` | 실험 확인 | 같음 | `t06-lambda.log` E1 |
| 비동기 재시도 횟수 | 기본 2회, 총 3회 (`lambda.md:135`) | OnFailure 레코드 `approximateInvokeCount=3`, `condition=RetriesExhausted`; `MaximumRetryAttempts=0` → 1 | 실험 확인 | 같음(재시도 간격은 0초로 줄여서 시험) | `t06-lambda.log` E2 |
| 함수 DLQ | 원래 payload + `RequestID`, `ErrorCode`, `ErrorMessage` 속성 (`lambda.md` Asynchronous Invocation Retries) | 본문 `id=x1`, `ErrorMessage`에 `boom-on-purpose` | 실험 확인 | 같음 | `t06-lambda.log` E2 |
| SQS ESM 실패 → redrive | 실패 batch는 VisibilityTimeout 뒤 재수신, RedrivePolicy 적용 (`lambda.md:1246`) | VisibilityTimeout 3, maxReceiveCount 2 → 약 9초 뒤 DLQ 1, main 0. 성공 함수는 0/0 | 실험 확인 | 같음 | `t06-lambda.log` E3 |
| ESM `ScalingConfig.MaximumConcurrency` | 저장만, poller는 ESM당 1개씩 (`lambda.md:1312`) | 실험하지 않음 | 확인 못 함 | 다름(문서) | — |
| S3 OnFailure destination | 전달 안 함 (`lambda.md` Asynchronous Invocation Destinations) | 실험하지 않음 | 확인 못 함 | 다름(문서) | — |

## KMS

| 서비스·기능 | 문서 주장 | 실험 결과 | 판정 | AWS와 같은가 | 근거 |
|---|---|---|---|---|---|
| key policy 평가 | 문서에 직접 문장 없음. `iam.md:2425`~ resource policy 목록(S3, SQS, SNS, Lambda, EventBridge, DSQL)에 KMS 없음 | IAM on: key policy `Deny Principal:* kms:Encrypt`인데 `kms:*` user Encrypt ALLOW. account root 문장을 뺀 key policy에서도 ALLOW | AWS와 다름(문서 언급 없음) | 다름 | `t07-iam.log` E1 |
| KMS identity policy 평가 | key ARN 기준 평가 (`kms.md` IAM Enforcement) | 정책 없는 `gus` Encrypt → `AccessDeniedException` | 실험 확인 | 같음 | `t07-iam.log` E1 |
| grant | "Grants are stored and queryable but are not evaluated during crypto operations." (`kms.md:229`) | `gus`에게 Encrypt grant(ListGrants 1개) → on에서 `AccessDeniedException` | 실험 확인 | 다름 | `t07-iam.log` E2 |
| encryption context | AAD에 context 지문 포함, 다르면 `InvalidCiphertextException` (`kms.md` Symmetric Ciphertext Envelope) | 같은 context 복호화 성공, 다른 context·context 없음 `InvalidCiphertextException`, `DisableKey` 뒤 `DisabledException` | 실험 확인 | 같음 | `t07-*.log` E3 |

## CloudFormation

| 서비스·기능 | 문서 주장 | 실험 결과 | 판정 | AWS와 같은가 | 근거 |
|---|---|---|---|---|---|
| create 실패 rollback | 실패 시 `ROLLBACK_IN_PROGRESS` → `ROLLBACK_COMPLETE` (`cloudformation.md` Stack status events) | `DelaySeconds: 5000` queue 실패 → `ROLLBACK_COMPLETE`, 먼저 만든 queue 삭제됨 | 실험 확인 | 같음 | `t08-cfn.log` E1 |
| `OnFailure=DO_NOTHING` | 문서에 언급 없음 | `CREATE_FAILED`가 아니라 `ROLLBACK_COMPLETE`, 먼저 만든 queue도 삭제됨 | AWS와 다름(문서 언급 없음) | 다름 | `t08-cfn.log` E1 |
| update 실패 rollback | "When an update fails, Floci rolls back the resources it changed." (`cloudformation.md:1052`) | `UPDATE_ROLLBACK_COMPLETE`, VisibilityTimeout 60 → 30 복원, 새 queue 없음 | 실험 확인 | 같음 | `t08-cfn.log` E2 |
| 모르는 resource type | "Resource type AWS::Fake::Thing is not supported by Floci. It was stubbed and nothing was created for it." (`cloudformation.md:257`) | `CREATE_COMPLETE`, 이벤트 사유에 같은 문장 | 실험 확인 | 다름(AWS는 실패) | `t08-cfn.log` E3 |
| SQS `VisibilityTimeout` 상한(43200) | 문서에 언급 없음 | `CreateQueue VisibilityTimeout=99999`가 ALLOW (CloudFormation과 직접 호출 둘 다) | AWS와 다름(문서 언급 없음) | 다름 | 실험 중 관찰(dev 로그, 스크립트에 고정하지 않음) |

## Cognito / API Gateway / EKS IRSA

| 서비스·기능 | 문서 주장 | 실험 결과 | 판정 | AWS와 같은가 | 근거 |
|---|---|---|---|---|---|
| REST Cognito authorizer | 토큰 없음·무효·다른 pool → 401 (`api-gateway.md:386`) | 없음/엉터리/다른 pool 401, 정상 IdToken 200 | 실험 확인 | 같음 | `t09-*.log` E1 |
| `AWS_IAM` 메서드 서명 검증 | SigV4 검증, 실패 403 (`api-gateway.md:271`~) | 서명 없음 403, 틀린 secret 403, `test` 서명 200 | 실험 확인 | 같음 | `t09-*.log` E2 |
| `AWS_IAM` 인가 | "Floci authenticates the caller but does not authorize the call" (`api-gateway.md:334`) | IAM on에서 정책 없는 user 서명 → 200 | 실험 확인 | 다름 | `t09-iam.log` E2 |
| IRSA 정상 토큰 | 서명·iss·aud·exp·trust 조건 검사 (`eks.md:938`~) | `app:reader` ALLOW, `SubjectFromWebIdentityToken=system:serviceaccount:app:reader` | 실험 확인 | 같음 | `t10-*.log` E1 |
| IRSA trust `sub` 불일치 | 403 `AccessDenied` | `app:writer` `AccessDenied` (off/on) | 실험 확인 | 같음 | `t10-*.log` E1 |
| IRSA 서명 변조 / aud 불일치 | `InvalidIdentityToken` (400) | 둘 다 `InvalidIdentityToken` (off/on) | 실험 확인 | 같음 | `t10-*.log` E1 |
| floci가 호스팅하지 않는 issuer | `eks.md:946` "treated as opaque and accepted … requires no configuration flag" / `sts.md:327` "When `FLOCI_SERVICES_IAM_ENFORCEMENT_ENABLED=true`, those tokens return `InvalidIdentityToken`" | off: ALLOW / on: `InvalidIdentityToken` | 실험 확인 (`sts.md` 기준. `eks.md:946`은 enforcement 조건을 빠뜨림) | off는 다름 | `t10-*.log` E2 |

## 문서만 읽고 실험하지 않은 관련 항목

| 서비스·기능 | 문서 주장 | 판정 |
|---|---|---|
| EventBridge target `RoleArn` | "Other target types store the role as configuration without assuming it or enforcing its IAM policies." (`eventbridge.md:304`) | 확인 못 함 |
| API Gateway REST API resource policy | "API Gateway REST API policies are stored but not evaluated." (`iam.md:2438`) | 확인 못 함 |
| Lambda function policy (`AddPermission`) | enforcement에서 평가, `PrincipalOrgID` 조건은 아무도 허용 안 함 (`lambda.md` Function policies under IAM enforcement) | 확인 못 함 |
| SNS topic policy, DSQL cluster policy | resource policy로 평가 (`iam.md:2434`, `:2435`) | 확인 못 함 |
| KMS AWS managed key | key policy는 표준 account-root 정책, `kms:ViaService` 조건 없음 (`kms.md:221`) | 확인 못 함 |
| CloudFormation `SetStackPolicy` | 구조만 검사, 강제 안 함 (`cloudformation.md:46`) | 확인 못 함 |
| HTTP API(v2) JWT authorizer + Cognito | 사설 주소 issuer는 `FLOCI_SECURITY_ALLOW_PRIVATE_JWT_TARGETS=true` 필요 (`api-gateway.md:8`~) | 확인 못 함 |

## 서버리스 연결 (2026-11-13 추가)

strict(`LAB_IAM`+`LAB_SIG`+`LAB_S3AUTH`)와 IAM off 대조. 상세 표와 함정 카드는 `curriculum-serverless.md` "검증 결과" 절, 로그는 `lab/logs/sl-1/`, `sl-2/`.

| 서비스·기능 | 문서 주장 | 실험 결과 | 판정 | AWS와 같은가 | 근거 |
|---|---|---|---|---|---|
| Lambda 실행 role → 함수 코드 안 DynamoDB 호출 | 알려진 role이면 그 role의 임시 자격증명 주입, enforcement가 role 정책 평가 (`lambda.md` Real AWS Credentials) | Allow 없음·명시 Deny → handler 안 `AccessDeniedException`, Allow → OK, 신원 `assumed-role/<role>/<fn>` | 실험 확인 | 같음 | `sl4-strict.log` W2 |
| Lambda 호출자 권한 | (IAM enforcement) | `lambda:InvokeFunction` 없는 user `AccessDeniedException` | 실험 확인 | 같음 | `sl1-strict.log` W0 |
| Lambda START/END/REPORT 로그 | `lambda.md:1010` 포함된다고 함 | handler 출력만 | 문서와 다름 | 다름 | `sl1-*.log` W9 |
| Lambda timeout 로그 | 언급 없음 | 함수 로그에 없음 | AWS와 다름(문서 언급 없음) | 다름 | `sl1-*.log` W9 |
| `logs:FilterLogEvents` 인가 | `iam.md:1820` Logs ARN을 floci가 만든다 | `resource=*`로 평가, log-group ARN Allow는 거부 | 문서와 다름 | 다름 | `sl1-strict.log`, `.floci.log` |
| 실행 role 로그 전송 권한 | 언급 없음 | 권한 없어도 로그 남음 | AWS와 다름(문서 언급 없음) | 다름 | `sl1-*.log` W9 |
| warm 재사용·동시 호출·idle 회수 | `CONTAINER_IDLE_TIMEOUT_SECONDS`, warm pool (`lambda.md` Configuration) | 연속 같은 env, 겹친 호출 새 env, idle 20초 설정 후 새 env | 실험 확인 | 메커니즘 같음(회수 시점은 AWS 비공개) | `sl2-strict.log` W10 |
| provisioned concurrency | "Each environment runs the real function initialization", spillover (`lambda.md` Provisioned concurrency) | READY 후 첫 호출 init 완료·`provisioned-concurrency`, 두 번째 겹친 호출 on-demand cold | 실험 확인 | 같음 | `sl2-strict.log` W11 |
| on-demand `AWS_LAMBDA_INITIALIZATION_TYPE` | provisioned 값만 언급 | 빈 문자열 | AWS와 다름(문서 언급 없음) | 다름 | `sl2-strict.log` W11 |
| API Gateway `AWS_PROXY` 데이터 경로 | `AWS_PROXY` ✅ (`api-gateway.md:422`) | path·query·header·body·method 전달, Lambda status·header 그대로, 예외 502·재시도 없음 | 실험 확인 | 같음 | `sl3-*.log` W1 |
| API Gateway → Lambda 함수 policy | 언급 없음 | 없음·틀린 SourceArn도 201 | AWS와 다름(문서 언급 없음) | 다름 | `sl3-*.log` W1 |
| 잘못된 proxy 응답 | `api-gateway.md:393` INTEGRATION_FAILURE | 200, 빈 body | 문서와 다름 | 다름 | `sl3-*.log` W1 |
| DynamoDB 조건부 쓰기 | (DynamoDB API) | overwrite / 조건 거부 / 동시 5개 중 1개 / 조건부 전이 1회 | 실험 확인 | 같음 | `sl4-*.log` W3a |
| SQS ESM 재수신 → DLQ, 최소 중복 처리 | `lambda.md:1246` | 실패 handler 3회 후 DLQ 1, 쓰기 후 실패·중복 메시지 모두 `PAID/1` | 실험 확인 | 같음 | `sl5-*.log` W8c, D |
| ESM 실행 role queue 권한 | 언급 없음 | 권한 없어도 ESM 생성·소비 | AWS와 다름(문서 언급 없음) | 다름 | `sl5-strict.log` W8c |
| async OnFailure 실행 role 권한 | 언급 없음 | 권한 없어도 전달 | AWS와 다름(문서 언급 없음) | 다름 | `sl5-strict.log` W8b |
| reserved concurrency, async retry (strict) | `lambda.md:413`, `:135` | 1/2, 3/1 (t06과 같음) | 실험 확인 | 같음 | `sl5-*.log` W8a·b |
