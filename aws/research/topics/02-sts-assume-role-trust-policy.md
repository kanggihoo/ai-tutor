# 02. STS AssumeRole과 trust policy (principal, 양쪽 허용, ExternalId)

## ① 배울 것
role을 빌려 쓰려면 role 쪽 trust policy와 호출자 쪽 identity policy가 둘 다 허용해야 하고, `sts:ExternalId` 조건이 제3자 대리 호출(confused deputy)을 어떻게 막는지 거부 응답으로 확인한다.

## ② 왜 MinIO·PostgreSQL 등으로 안 되는가
MinIO의 STS는 OIDC/LDAP 로그인을 임시 키로 바꿔 줄 뿐, "다른 주체가 정의한 role을 trust policy 조건 아래에서 빌린다"는 모델이 없다. PostgreSQL `SET ROLE`은 같은 DB 안의 role 멤버십이고, 상대방이 받아들일지를 정하는 trust 문서와 ExternalId 같은 조건이 없다. 계정 사이 위임과 서비스 principal(`lambda.amazonaws.com`)이 role을 받는 구조는 AWS에만 있다.

## ③ floci 검증 결과와 판정
실험: `lab/t02_sts_trust.py` (case `t02-off`, `t02-iam`). 기대값 출처: [ExternalId](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user_externalid.html), [cross-account evaluation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic-cross-account.html), [AssumeRole DurationSeconds](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html).

| 확인한 것 | off | on | 판정 |
|---|---|---|---|
| trust에 있고 identity도 허용하는 `alice` | ALLOW | ALLOW | 실험 확인 |
| trust에 없는 `bob` (identity는 `sts:AssumeRole` 허용) | ALLOW | `AccessDenied` | 실험 확인 |
| trust에 있지만 identity policy가 없는 `carol` | ALLOW | `AccessDenied` | 실험 확인 (`sts.md` "The caller's own identity policy must allow `sts:AssumeRole` too") |
| 없는 role | `AccessDenied` | `AccessDenied` | 실험 확인 (enforcement 무관) |
| trust가 `sts:ExternalId = ext-123` 요구: 없음 / `wrong` / `ext-123` | ALLOW / ALLOW / ALLOW | `AccessDenied` / `AccessDenied` / ALLOW | 실험 확인 |
| `DurationSeconds=7200`, role `MaxSessionDuration=3600` | ALLOW (만료 약 2시간 뒤) | ALLOW (만료 약 2시간 뒤) | **문서와 다름** |
| `DurationSeconds=50000` | `ValidationError` | `ValidationError` | 실험 확인 (API 상한 43200) |

문서와 다른 항목의 값 대조:

| | 문서 (`sts.md:278`) | 실제 |
|---|---|---|
| `AssumeRole` `DurationSeconds=7200` on role with `MaxSessionDuration=3600` | "`AssumeRole` rejects a `DurationSeconds` above the role's `MaxSessionDuration` with `ValidationError` (400) … checked even when IAM policy enforcement is disabled." | HTTP 200, `Credentials.Expiration`이 호출 시각 + 7200초 (`get_role`은 `MaxSessionDuration: 3600`을 돌려줌) |

## ④ floci에서 깨지거나 주의가 필요한 부분
- **세션 태그 조건이 맞지 않는다.** trust에 `aws:RequestTag/team = red`를 걸고 `Tags=[team=red]`로 assume하면 AWS는 허용하지만 floci는 `AccessDenied`다. 문서 원문(`sts.md:309`): "**Session tags and source identity are not modelled.** `aws:RequestTag/*`, `aws:TagKeys`, `sts:TransitiveTagKeys` and `sts:SourceIdentity` are not in the request context, so a condition on them does not match, and `sts:TagSession` and `sts:SetSourceIdentity` are not checked." 실험 판정: 실험 확인 (AWS와는 다름). ABAC(태그 기반 권한) 레슨은 이 환경에서 하지 않는다.
- **MFA 조건 Allow는 항상 거부된다.** `Bool aws:MultiFactorAuthPresent=true` 조건 Allow가 enforcement on에서 `AccessDenied`. 원문(`iam.md:1084`): "`aws:MultiFactorAuthPresent` and `aws:MultiFactorAuthAge` are never placed in the request context". 실험 확인.
- `MaxSessionDuration`이 걸리지 않으므로 "세션 길이 상한" 레슨은 하지 않는다.

## ⑤ 실습 스크립트
- `aws/research/lab/t02_sts_trust.py` — 실행: `./run.sh t02`

## ⑥ 예상 레슨 수와 순서 (3)
1. trust policy와 identity policy: 둘 중 하나만 있으면 왜 실패하는가 (`bob`, `carol` 장면)
2. ExternalId: 공급업체에 role을 내줄 때 없음 / 틀림 / 맞음 세 응답 비교
3. 서비스가 role을 받는 경우(Lambda 실행 role)로 연결, 06 주제와 이어 붙임
