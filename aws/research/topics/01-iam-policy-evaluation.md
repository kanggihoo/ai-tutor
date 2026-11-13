# 01. IAM 정책 평가 순서 (identity · explicit Deny · permission boundary · session policy · SCP)

## ① 배울 것
요청 하나가 허용되려면 어느 정책이 Allow를 주고 어느 정책이 상한을 거는지, 그리고 명시 Deny가 왜 모든 것을 이기는지를 실제 거부 응답으로 확인한다.

## ② 왜 MinIO·PostgreSQL 등으로 안 되는가
MinIO도 S3식 policy JSON을 받지만 permission boundary, session policy, SCP 같은 "상한" 개념이 없고 서비스가 S3 하나다. PostgreSQL의 GRANT/ROLE은 객체 권한 모델이라 "계정 → OU → 조직" 계층이나 AssumeRole 세션이라는 주체 자체가 없다. 같은 user가 S3는 되고 SQS는 거부되는 "서비스 경계를 넘는 하나의 인가 엔진"은 AWS 모델에만 있다.

## ③ floci 검증 결과와 판정
실험: `lab/t01_iam_eval.py` (case `t01-off`, `t01-iam`, `t01-iam-sig`), `lab/t04_scp.py` (case `t04-iam`, `t04-iam-scp`). 기대값 출처: [IAM policy evaluation logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html), [SCP](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html).

| 확인한 것 | enforcement off | enforcement on | 판정 |
|---|---|---|---|
| `alice`(s3:ListAllMyBuckets만 허용)가 `sqs:ListQueues` | ALLOW | `AccessDeniedException` (400) | 실험 확인 |
| access key `test`로 `sqs:ListQueues` | ALLOW | ALLOW | 실험 확인 (`iam.md:2482` "Always allowed — no policy lookup") |
| 존재하지 않는 `AKIA…` key | ALLOW | `UnrecognizedClientException` | 실험 확인 |
| `s3:*` Allow + `s3:CreateBucket` Deny → CreateBucket | ALLOW | `AccessDenied` (403) | 실험 확인 |
| identity `*` + boundary `sqs:*` → `s3:ListAllMyBuckets` | ALLOW | `AccessDenied` | 실험 확인 |
| role(`*`)을 session policy `s3:ListAllMyBuckets`로 assume → `sqs:ListQueues` | ALLOW | `AccessDeniedException` | 실험 확인 |
| 정책 없는 user로 14개 서비스 읽기 호출 (S3, SQS, SNS, DynamoDB, Lambda, KMS, Secrets Manager, SSM, EC2, IAM, EventBridge, Logs, CloudFormation, Step Functions) | 14개 모두 ALLOW | 14개 모두 거부 (`AccessDenied` / `AccessDeniedException` / SNS `AuthorizationError`) | 실험 확인 |
| 같은 user로 `sts:GetCallerIdentity` | ALLOW | ALLOW | 실험 확인 (`iam.md` Bypass rules) |
| member 계정 role session에 SCP `Deny s3:*` → `s3:ListAllMyBuckets` | SCP flag off: ALLOW | SCP flag on: `AccessDenied` | 실험 확인 |
| 같은 session의 `sqs:ListQueues` (SCP에 없음) | ALLOW | ALLOW | 실험 확인 |
| member 계정 bare 12자리 key(account root) → S3 | ALLOW | `AccessDenied` | 실험 확인 (`iam.md` "The account-root principal is subject to SCPs") |
| SCP를 root에 붙인 뒤 management 계정 user → S3 | ALLOW | ALLOW | 실험 확인 ("management account is exempt", `iam.md:2460`) |

## ④ floci에서 깨지거나 주의가 필요한 부분
- **서명 위조가 통과한다.** enforcement만 켜고 `FLOCI_AUTH_VALIDATE_SIGNATURES`를 끄면, alice의 access key ID에 엉터리 secret을 붙여도 `s3:ListAllMyBuckets`가 ALLOW다. floci가 access key ID만 보고 주체를 정하기 때문이다(`multi-account.md:31` "Account selection is AKID-based and is not proof that the caller possesses the corresponding secret."). 같은 호출이 `LAB_SIG=true`에서는 `SignatureDoesNotMatch`(S3), `InvalidSignatureException`(SQS)로 거부된다. 실습 compose에는 두 flag를 함께 켠다.
- access key `test`는 enforcement와 SCP 모두를 우회한다. 레슨에서는 항상 IAM user나 AssumeRole 세션으로 호출한다.
- MFA 조건키(`aws:MultiFactorAuthPresent`)는 채워지지 않아 MFA 조건 Allow는 절대 허용되지 않는다(02 주제 실험 E3). MFA 강제 정책은 이 환경에서 연습하지 않는다.
- 판정은 action·resource 매핑이 floci에 있는 경우에만 동작한다. "매핑할 수 없는 action은 허용"(`iam.md` Bypass rules "Unresolvable action | Allowed")이라, 레슨에서 쓰는 action은 위 14개처럼 실험으로 확인한 것으로 한정한다.

## ⑤ 실습 스크립트
- `aws/research/lab/t01_iam_eval.py`, `aws/research/lab/t04_scp.py`
- 실행: `cd aws/research/lab && ./run.sh t01` / `./run.sh t04`

## ⑥ 예상 레슨 수와 순서 (5)
1. identity policy Allow와 implicit deny (`alice`가 S3는 되고 SQS는 안 되는 장면)
2. explicit Deny가 Allow를 이기는 장면
3. permission boundary: Allow `*`인데 왜 S3가 막히는가
4. session policy: 같은 role이 세션마다 다른 권한을 갖는 장면
5. SCP: 조직 계층의 상한, management 계정 면제, account root도 묶인다는 점
