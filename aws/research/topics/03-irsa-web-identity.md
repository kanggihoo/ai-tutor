# 03. IRSA: OIDC 토큰으로 AWS role 받기 (AssumeRoleWithWebIdentity)

## ① 배울 것
Kubernetes service account가 발급받은 JWT 하나가 어떻게 AWS 자격증명으로 바뀌는지, 그리고 trust policy의 `sub`·`aud` 조건과 서명 검증이 어느 지점에서 요청을 거르는지 확인한다.

## ② 왜 MinIO·PostgreSQL 등으로 안 되는가
JWT 서명 검증 자체는 아무 라이브러리로도 연습할 수 있다. 이 주제에서 배울 것은 그 뒤 단계다. 외부 IdP 토큰의 `sub`를 AWS role의 trust policy 조건으로 매칭해, 장기 키 없이 pod 단위로 권한을 나누는 구조다. 이 연합(federation) 지점은 AWS STS에만 있다. MinIO STS는 자기 정책으로 매핑할 뿐 "다른 시스템(EKS)의 issuer를 IAM provider로 등록하고 role trust로 거른다"는 구조가 없다.

## ③ floci 검증 결과와 판정
실험: `lab/t10_irsa.py` (case `t10-off`, `t10-iam`). EKS는 mock 모드(`FLOCI_SERVICES_EKS_MOCK=true`, k3s 없음)이고 토큰은 floci 전용 엔드포인트 `POST /_floci/eks/clusters/lab/oidc-token`으로 받았다. 기대값 출처: [EKS IRSA](https://docs.aws.amazon.com/eks/latest/userguide/associate-service-account-role.html), [AssumeRoleWithWebIdentity](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithWebIdentity.html).

trust policy 조건: `oidc.eks.us-east-1.amazonaws.com/id/<id>:sub = system:serviceaccount:app:reader`, `:aud = sts.amazonaws.com`.

| 확인한 것 | off | on | 판정 |
|---|---|---|---|
| `app:reader` 토큰 | ALLOW, `SubjectFromWebIdentityToken = system:serviceaccount:app:reader` | 같음 | 실험 확인 |
| `app:writer` 토큰 | `AccessDenied` | `AccessDenied` | 실험 확인 (enforcement 무관) |
| 서명 첫 글자를 바꾼 토큰 | `InvalidIdentityToken` | `InvalidIdentityToken` | 실험 확인 |
| `audience=something-else`로 받은 토큰 | `InvalidIdentityToken` | `InvalidIdentityToken` | 실험 확인 |
| floci가 호스팅하지 않는 issuer(`https://issuer.example.com`)의 서명 없는 토큰 | ALLOW | `InvalidIdentityToken` | 실험 확인 (`sts.md:327`) |

문서끼리 어긋난 곳: `eks.md:946`은 "A token whose issuer Floci does not host is treated as opaque and accepted … requires no configuration flag."라고만 쓰고, `sts.md:327`은 "When `FLOCI_SERVICES_IAM_ENFORCEMENT_ENABLED=true`, those tokens return `InvalidIdentityToken`"이라고 쓴다. 실험 결과는 `sts.md` 쪽과 같다(on에서 `InvalidIdentityToken`).

## ④ floci에서 깨지거나 주의가 필요한 부분
- 토큰을 floci의 `_floci/…` 엔드포인트에서 받는다. 실제 EKS에서는 kubelet이 projected volume으로 넣어 주는 파일이다. 레슨에서 이 차이를 처음에 한 줄로 밝힌다.
- enforcement가 꺼져 있으면 아무 문자열 토큰(외부 issuer)도 통과한다. 실습은 enforcement on으로만 한다.
- real 모드(k3s 컨테이너)로 pod 안에서 토큰을 쓰는 흐름은 돌려 보지 않았다(확인 못 함). 무거운 k3s 없이 mock으로 충분하다고 판단했다.

## ⑤ 실습 스크립트
- `aws/research/lab/t10_irsa.py` — 실행: `./run.sh t10`

## ⑥ 예상 레슨 수와 순서 (2)
1. issuer → OIDC provider → trust policy `sub`/`aud` 조건, reader는 되고 writer는 안 되는 장면
2. 토큰 변조·aud 불일치·외부 issuer가 각각 어느 단계에서 거부되는가 (`InvalidIdentityToken` vs `AccessDenied`의 차이)
