# 07. 사용자 인증에서 API 호출까지: Cognito user pool → API Gateway authorizer, AWS_IAM 메서드

## ① 배울 것
API Gateway가 요청을 integration에 넘기기 전에 Cognito 토큰을 어떻게 검사하는지, 그리고 `AWS_IAM` 메서드에서 "서명이 맞다(인증)"와 "호출해도 된다(인가)"가 다른 단계라는 것을 응답 코드로 확인한다.

## ② 왜 MinIO·PostgreSQL 등으로 안 되는가
JWT 검사만이면 nginx나 Spring Security로도 연습할 수 있다. AWS에서만 배울 수 있는 부분은 연결 방식이다. 코드 없이 `COGNITO_USER_POOLS` authorizer를 메서드에 붙이면 게이트웨이가 pool의 JWKS로 검사한다. `AWS_IAM` 메서드는 SigV4 서명과 IAM 정책(`execute-api:Invoke`)으로 API를 보호한다. 이 두 장치가 managed 게이트웨이 설정으로만 존재한다.

## ③ floci 검증 결과와 판정
실험: `lab/t09_authn.py` (case `t09-off`, `t09-iam`). REST API(v1), MOCK integration, stage `dev`, 호출 URL `http://floci:4566/restapis/<id>/dev/_user_request_/<path>`. 기대값 출처: [Cognito authorizer](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html), [API Gateway IAM permissions](https://docs.aws.amazon.com/apigateway/latest/developerguide/permissions.html).

| 확인한 것 | IAM off | IAM on | 판정 |
|---|---|---|---|
| `/open` (NONE), 토큰 없음 | 200 | 200 | 실험 확인 |
| `/secure` (Cognito), 토큰 없음 | 401 | 401 | 실험 확인 |
| `/secure`, `abc.def.ghi` | 401 | 401 | 실험 확인 |
| `/secure`, 다른 user pool의 IdToken | 401 | 401 | 실험 확인 |
| `/secure`, 같은 pool의 IdToken (`USER_PASSWORD_AUTH`로 받음) | 200 | 200 | 실험 확인 |
| `/iam` (AWS_IAM), 서명 없음 | 403 | 403 | 실험 확인 |
| `/iam`, `test`/`test`로 서명 | 200 | 200 | 실험 확인 |
| `/iam`, 정책 없는 IAM user로 서명 (AWS라면 on에서 403) | 200 | 200 | 실험 확인 (`api-gateway.md:334`) |
| `/iam`, 그 user의 key + 틀린 secret | 403 | 403 | 실험 확인 |

## ④ floci에서 깨지거나 주의가 필요한 부분
- **`AWS_IAM` 메서드는 인증만 하고 인가하지 않는다.** 원문(`api-gateway.md:334`): "Floci authenticates the caller but does not authorize the call: it does not evaluate `execute-api:Invoke` against the caller's IAM policies or a resource policy, so any validly signed, known caller is let through." REST API resource policy도 "stored but not evaluated"(`iam.md:2438`). 그래서 이 주제의 IAM 부분은 "서명 검증이 어디서 일어나는가"까지만 가르치고, `execute-api:Invoke` 정책 레슨은 하지 않는다.
- API Gateway는 서명을 자체 검증하므로 `FLOCI_AUTH_VALIDATE_SIGNATURES` 없이도 틀린 secret이 403이다. 01 주제의 S3·SQS와 동작이 다르다.
- HTTP API(v2) JWT authorizer는 Cognito issuer가 사설 주소라 `FLOCI_SECURITY_ALLOW_PRIVATE_JWT_TARGETS=true`가 필요하다고 문서에 있다(`api-gateway.md` "JWT issuer network policy"). 실험하지 않았다(확인 못 함).
- Cognito identity pool(user pool 토큰을 AWS 자격증명으로 바꾸는 것)은 문서를 읽지 않았고 실험하지 않았다(확인 못 함). `api-gateway.md`에 "`cognitoIdentity` are always null"이라는 문장이 있다.
- 실제 Lambda authorizer(TOKEN/REQUEST)는 시험하지 않았다(확인 못 함).

## ⑤ 실습 스크립트
- `aws/research/lab/t09_authn.py` — 실행: `./run.sh t09`

## ⑥ 예상 레슨 수와 순서 (2)
1. user pool → app client → 로그인 → IdToken → Cognito authorizer: 없음/엉터리/다른 pool/정상 네 응답
2. AWS_IAM 메서드: 서명 없음 403, 틀린 서명 403, 맞는 서명 200, 그리고 "정책이 없어도 200"이 floci의 한계이고 AWS에서는 403이라는 점
