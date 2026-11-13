# 04. Resource policy와 공개 접근 (bucket policy, 계정 위임, Block Public Access)

## ① 배울 것
같은 계정 안에서 bucket policy가 identity policy 없이도 접근을 주는 경우와 주지 못하는 경우(계정만 지목한 위임)를 구분하고, 익명 요청과 Block Public Access가 어떻게 판정되는지 확인한다.

## ② 왜 MinIO·PostgreSQL 등으로 안 되는가
MinIO도 bucket policy와 익명 접근을 지원하므로 "공개 읽기" 자체는 MinIO로 연습할 수 있다. 이 주제가 AWS에서만 의미 있는 부분은 두 정책의 합성이다. resource policy가 `user/dave`를 지목하면 identity 없이 허용되고, `:root`(계정)만 지목하면 identity policy가 있어야 허용된다(위임). 이 규칙은 IAM 평가 엔진과 계정 개념이 있어야 생긴다. 그래서 범위를 정책 합성과 Block Public Access로 좁힌다.

## ③ floci 검증 결과와 판정
실험: `lab/t03_resource_policy.py` (case `t03-off`, `t03-iam`, `t03-s3auth`). 기대값 출처: [account principal](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html#principal-accounts), [cross-account evaluation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic-cross-account.html), [Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html).

bucket policy: `dave`에게 GetObject Allow, 계정 root에게 GetObject Allow, `frank`에게 GetObject Deny.

| 확인한 것 | off | IAM on | S3 ENFORCE_AUTH만 on | 판정 |
|---|---|---|---|---|
| `dave` (identity 없음, policy가 이름으로 지목) | ALLOW | ALLOW | ALLOW | 실험 확인 |
| `erin` (identity 없음, policy는 계정 root만 지목) | ALLOW | `AccessDenied` | ALLOW | 실험 확인. IAM on은 위임 규칙(`iam.md` "within the account it grants nothing on its own"), ENFORCE_AUTH만이면 "For bucket owners … default decision is **Allow**"(`s3.md:461`) |
| `frank` (identity `s3:*`, policy가 명시 Deny) | ALLOW | `AccessDenied` | `AccessDenied` | 실험 확인 |
| 익명 GET, 비공개 bucket | 200 | **200** | 403 | 실험 확인. IAM filter는 REST 요청을 검사하지 않는다(`iam.md:3070` "**REST requests are not checked.**") |
| 익명 GET, public-read bucket policy | 200 | 200 | 200 | 실험 확인 |
| 새 bucket의 `GetPublicAccessBlock` | 네 값 모두 true | 같음 | 같음 | 실험 확인 |
| 새 bucket(설정 안 함)에 public bucket policy | ALLOW | ALLOW | ALLOW | **문서와 다름** |
| `PutPublicAccessBlock`(네 값 true) 후 public bucket policy | `AccessDenied` | 같음 | 같음 | 실험 확인 (`s3.md:502`) |

문서와 다른 항목의 값 대조:

| | 문서 (`s3.md:504`) | 실제 |
|---|---|---|
| 아무 설정 안 한 bucket에 `Principal:"*"` GetObject policy | "A bucket nobody configured enforces the default `GetPublicAccessBlock` reports for it: all four settings on." → `AccessDenied` 예상 | `PutBucketPolicy` 성공(에러 없음). 같은 bucket의 `GetPublicAccessBlock`은 네 값 모두 `true`를 돌려준다 |

## ④ floci에서 깨지거나 주의가 필요한 부분
- **다른 계정 SQS 접근이 문서대로 동작하지 않는다(cross-account 레슨 불가).** 계정 `111111111111`의 user가 계정 `000000000000`의 queue에 `SendMessage`할 때:

  | | 문서 (`sqs.md:220`) | 실제 (IAM on) |
  |---|---|---|
  | identity `sqs:*`, queue policy 없음 | queue policy와 identity가 둘 다 허용해야 함 → 거부 예상 | ALLOW, 메시지가 A의 queue에 들어감 (A queue 메시지 수 1) |
  | identity가 A의 queue ARN만 허용 + queue policy가 그 user 지목 | 둘 다 허용 → ALLOW 예상 | `AccessDeniedException` |
  | floci 로그 | | `IAM enforcement DENY: … action=sqs:SendMessage resource=arn:aws:sqs:us-east-1:111111111111:shared-q` |

  IAM filter가 queue ARN을 queue 주인(000000000000)이 아니라 호출자 계정(111111111111)으로 만든다. 그래서 queue policy가 판정에 쓰이지 않는다. cross-account resource policy는 이 환경에서 가르치지 않는다.
- 익명 접근을 막으려면 `FLOCI_SERVICES_S3_ENFORCE_AUTH=true`가 따로 필요하다. IAM enforcement만으로는 익명 GET이 200이다.
- 새 bucket의 기본 Block Public Access가 실제로는 걸리지 않으므로, 레슨에서는 `PutPublicAccessBlock`을 명시적으로 호출한 뒤 시연한다.
- S3 다른 계정 bucket 접근(`FLOCI_SERVICES_S3_GLOBAL_BUCKET_NAMESPACE`)은 실험하지 않았다(확인 못 함).

## ⑤ 실습 스크립트
- `aws/research/lab/t03_resource_policy.py` — 실행: `./run.sh t03`

## ⑥ 예상 레슨 수와 순서 (3)
1. bucket policy가 이름으로 지목하면 identity 없이 허용 (`dave`)
2. 계정만 지목하면 위임이라 identity가 필요 (`erin`), 명시 Deny는 어디에 있든 이긴다 (`frank`)
3. 익명 요청과 Block Public Access: ENFORCE_AUTH on/off, 명시적 PutPublicAccessBlock
