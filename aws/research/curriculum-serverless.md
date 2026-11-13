# `aws/` 과목 커리큘럼안: 서버리스 중심 (2026-11-12)

> 상태: Claude·Codex 토론 합의안이며 사용자 승인 전이다. 기본 단계 검증(W0·W1·W2·W3a·W8·W9·W10·W11·W12, D 최소 중복 확인)은 2026-11-13에 돌렸다(아래 "검증 결과"). C단계는 2026-11-13 사용자 요청으로 "DynamoDB 사용법"에서 "실행 role과 IAM 연계"로 바뀌었고, 새 층의 검증 W13·W14는 미실행. 확장용 W3b·W3c·W4~W7은 미결.
> 근거: `.herdr-discuss/20261112-1513-aws-topics/summary.md`(권한 중심안·레슨 형식), `.herdr-discuss/20261112-1603-aws-serverless/summary.md`(서버리스안), `.herdr-discuss/20261112-1741-aws-coldstart/summary.md`(cold start 추가·멱등성 축소). `.herdr-discuss/`는 git에서 제외된 로컬 폴더다.

## 왜 바뀌었나

조사 결론(`README.md`)의 7개 주제는 5개가 IAM 권한이었다. 사용자가 "권한 말고는 없네"라고 했고, 서버리스를 물었으며, CI/CD는 하지 않겠다고 했다. 또 멱등성은 distsys 등에서 이미 다루니 cold start 해결이 더 중요하다고 했다. 그래서 과목 축을 "주문 API 하나를 서버리스로 키우는 실행 예제"로 바꾸고, 권한은 서비스를 잇는 지점에서 다룬다.

"AWS로 뭘 많이 하나"에 대한 답: 사용량 순위는 조사하지 않았다. 용도로 보면 서버·컨테이너 앱 운영(EC2·ECS·EKS·RDS), 서버리스 API·이벤트 처리(Lambda·API Gateway·DynamoDB·SQS·EventBridge), 파일 보관·배포(S3·CloudFront), 데이터 저장·분석이 있다. 이 과목은 그중 서버리스의 "관리형 호출·저장·실패 처리 연결"을 floci로 배운다. EC2·ECS·RDS를 뺀 이유는 가치가 낮아서가 아니라, floci가 failover·쿼터 같은 운영 동작을 재현하지 않고 이번 범위가 아니어서다.

## 기본 단계

| 단계 | 서비스 | 배울 것 | 권한이 나오는 곳 | 열기 전 검증 |
|---|---|---|---|---|
| A 함수 실행 | Lambda, CloudWatch Logs | handler·event·context, timeout, 로그(`/aws/lambda/<name>`)로 한 요청 추적 | 호출자와 실행 role은 다른 주체, Allow·implicit deny·explicit Deny | W0, W9 |
| A' 실행 환경 수명과 cold start | Lambda (provisioned concurrency) | Init → Invoke(호출 사이 freeze) → 회수, 초기화 코드는 초기화 때만 실행되고 warm 재사용에서는 반복 안 함, 동시 요청이 늘면 새 환경, 회수 시점은 보장 안 됨, 완화책 다섯 가지 비교 | — | W10, (provisioned) W11, (로그) W12 |
| B HTTP 주문 API | API Gateway REST v1 `AWS_PROXY`, Lambda | HTTP 요청이 event로 바뀌는 계약, 응답 형식, 500(호출 거부)과 502(handler 오류·잘못된 응답), 재시도 없음 | API Gateway가 함수를 부를 권한(resource policy, SourceArn) | W1 |
| C 실행 role의 최소 권한과 세밀한 인가 | Lambda 실행 role, IAM, DynamoDB(인가 대상) | 함수 코드가 다른 서비스를 부를 때 실행 role로 판정됨 → 자원 범위(특정 table만) → 동작 범위(읽기만) → 항목 단위(`dynamodb:LeadingKeys` + 정책 변수로 자기 key만, 멀티테넌트 격리) → (선택) 속성 단위(`dynamodb:Attributes`). DynamoDB 사용법은 table 하나에 `GetItem`·`PutItem`만 | 이 단계 전체가 권한 | W2 (1층), W13 (2·3층), W14 (4층) |
| D 접수와 후처리 분리 | SQS, Lambda ESM | `202 접수 ≠ 완료`, 재수신이 생기는 AWS 쪽 원인(visibility timeout, ESM 실패 시 batch 반환), DLQ, 조건부 쓰기 한 번으로 중복 적용 막기(복습, DynamoDB 조건부 쓰기는 여기서만 등장), 재시도에도 유지되는 클라이언트 orderId | producer SendMessage와 consumer 실행 role 분리 | W8(ESM), 최소 중복 확인 |
| E 실패와 부하 | Lambda 동시성, async invoke | reserved concurrency 429, async 재시도·OnFailure, 호출 경로 세 가지(동기·ESM·async)의 재시도 주체와 실패 기록 위치 비교 | — | W8 |

### A'의 완화책 표

| 선택 | 바꾸는 것·한계 |
|---|---|
| static init 줄이기 | 초기화 작업 자체 축소. floci는 import를 흉내 낸 sleep 유/무와 init/warm 경로만 비교 |
| 메모리 조절 | CPU 등 자원 배분과 실행 시간의 trade-off. floci 비례 효과 실습은 제외 |
| provisioned concurrency | 지정 수의 초기화를 앞당김. 초과 호출 spillover와 추가 비용이 남음. reserved concurrency는 사전 초기화가 아님 |
| SnapStart | publish 시 초기화한 snapshot에서 새 환경 복구. provisioned concurrency와 병용 불가. floci 효과는 미확인 |
| queue로 분리 | 사용자 응답 경로에서 작업 대기를 분리. worker의 cold start 자체는 남음 |

주기적 호출로 warm을 유지할 수 있다고 가르치지 않는다. AWS가 회수 시점을 보장하지 않는다.

## 확장 (사용자에게 필요를 묻고 붙임)

| 확장 | 배울 것 | 검증 |
|---|---|---|
| EventBridge fan-out (우선) | 주문 이벤트 하나를 독립 업무 여럿이 받기, 규칙 매칭, 대상별 retry·DLQ. 도입부에서 경쟁 소비(한 queue에 worker 여럿)와 비교 | W4 |
| DynamoDB Streams형 접수 (우선) | Streams = table 항목이 바뀔 때마다 `INSERT`·`MODIFY`·`REMOVE` 기록(이전 값·새 값)을 순서대로 남기는 기능. Lambda가 이 기록을 받아 후처리. API는 DB에 한 번만 쓰므로 D의 dual-write(저장됐는데 메시지 없음)가 없어짐. distsys의 CDC를 AWS 기능으로 대응. 주의: 같은 기록이 두 번 올 수 있음, 후처리가 같은 table을 고치면 `MODIFY`가 다시 함수를 부르는 반복, floci는 기록을 메모리에만 둠(재시작 시 소실). C단계의 실행 role 권한(`dynamodb:GetRecords` 등)과 이어짐 | W5 |
| cold start 실측 | 실제 AWS에서 cold/warm, 메모리, provisioned 유무별 `Init Duration` 비교 | 실제 AWS 계정 승인 필요 |
| GSI·TTL | 고객별 조회 index, 만료와 물리 삭제의 차이(floci GSI는 즉시 일관·즉시 ACTIVE라 AWS와 다름) | W3b, W3c |
| Step Functions | 여러 Lambda를 Retry/Catch로 묶기 | W6 |
| Cognito → API Gateway authorizer | 로그인 토큰으로 API 보호 | 기존 `t09` 확인 |
| partial batch | `ReportBatchItemFailures` | W7 |
| SAM | 앞서 손으로 만든 연결이 템플릿에서 무엇으로 자동 생성되는지 | SAM 지원 검증 |
| 권한 심화 | STS 직접 AssumeRole·ExternalId, permission boundary·session policy, SCP, IRSA | 기존 `t01`~`t04`, `t10` + 직전 V 목록 |
| Security Group | VPC/private backend에 관심 있을 때 | 기존 `t05` |

## 다루지 않음

CI/CD(사용자 결정). EC2·ECS·RDS 운영 심화, VPC 라우팅·NACL, KMS key policy·grant, SQS cross-account(floci 재현 불가, `README.md`). 지연·비용·리전 장애·쿼터의 실측(floci 비재현, 실제 AWS는 승인 전 미개설). 멱등성 상세 과제(distsys에서 다룸).

## 레슨 진행과 환경 (권한 중심안에서 그대로 가져옴)

- 한 레슨: 요청 조건 제시(주체 → 서비스·자원 → action, 새 용어 한 줄) → 예측(구체 값: item 값, 호출 횟수, initId, DLQ 건수) → 실행 → 대조 → 왜(한 조건만 바꾼 요청). 이해 못 함 신호가 나오면 루트 규칙대로 중단.
- 공통 질문: "AWS가 대신 해 주는 것과 내가 책임질 것".
- floci와 AWS가 다른 동작은 그 레슨의 판단을 바꾸는 것만 "floci 결과 X / AWS 동작 Y (URL)" 한 줄 카드로.
- 자원은 tutor가 주는 boto3 setup으로 연결을 하나씩 만들고, handler는 Python 뼈대를 learner가 몇 줄만 고친다.
- 환경: `lab/compose.yml`의 digest 고정 floci, strict(IAM + 서명 검증 + S3 인가), `test` key는 bootstrap에만. 수업 runner는 lab 소유 자원만 정리한다(현재 `run.sh`의 전역 `floci-*` 정리는 수업용으로 쓰지 않는다).

## 검증 목록

| W | 내용 | 여는 단계 |
|---|---|---|
| W0 | 같은 event로 정상 / timeout, 응답 payload·`FunctionError`·자원 변경 구분 | A |
| W9 | 정상 호출 로그, ESM 실패 로그, 실행 role의 log 전송 권한 유/무, 조회 주체 권한 유/무 | A |
| W10 | static init의 `initId`·호출 count로 연속 / 겹친 burst(reserved 해제) / idle 회수 후 호출 관찰. 새 init 수는 기존 warm 수에 따라 달라짐 | A' |
| W11 | published version + alias, SnapStart off, PC=1 `READY` 후 호출: init이 이미 끝났는지, `AWS_LAMBDA_INITIALIZATION_TYPE`, 한 호출을 잡아 둔 채 spillover | A'(provisioned) |
| W12 | 로그와 initId·request ID 연결, `Init Duration` 유무만으로 판정하지 않음 | A'(로그) |
| W1 | `AWS_PROXY` path/query/header/body, 정상 / handler 예외 / 잘못된 응답(500·502), `AddPermission` 없음 / 맞는·다른 SourceArn, handler 실제 호출 여부 | B |
| W2 | 실행 role PutItem Allow 없음 / 있음 / 명시 Deny | C (1층) |
| W13 | 같은 함수·입력으로 실행 role 정책만 바꿈: `Orders`만 허용 → `Payments` 거부, `GetItem`만 허용 → `PutItem` 거부 (미실행) | C (2·3층) |
| W14 | `dynamodb:LeadingKeys` 조건: IAM user `kim`·`lee`에 `${aws:username}` 정책 하나로 자기 key만 Get/Put, 남의 key 거부, `Query`도 같은 판정. 실행 role은 role tag(`aws:PrincipalTag/tenant`)로 같은 격리. `Scan`은 floci 미지원(`iam.md:2983`)이라 카드 (미실행) | C (4층) |
| W3a | 조건 없는 overwrite vs 조건부 중복 거부 | D (복습용) |
| W8 | strict에서 reserved concurrency, async retry 2/0, SQS ESM 성공/실패 재확인 | D, E |
| W3b·W3c·W4·W5·W6·W7 | 확장별(위 표) | 해당 확장 (미실행) |

## floci 함정 카드 후보 (문서 기준)

- S3 이벤트 알림: 목적지 resource policy를 검사하지 않음(`floci-docs/services/s3.md` Event Notifications)
- EventBridge target `RoleArn`: assume하지 않음(`eventbridge.md:304`)
- API Gateway integration `credentials`: assume하지 않음(`api-gateway.md:549`), `AWS_IAM` 메서드는 인증만(`api-gateway.md:334`, `t09-iam.log`)
- Step Functions Retry 간격 30초 cap
- SQS ESM `MaximumConcurrency` 저장만(`lambda.md:1312`), `InvokeWithResponseStream` 없음
- DynamoDB native GSI: index 미저장·즉시 일관·즉시 ACTIVE(`dynamodb.md:375~381`), TTL 60초 sweep
- SNS → SQS 재시도: 3회 즉시(`sns.md:151~155`)
- Lambda init 시간 초과: AWS는 handler timeout을 잠식, floci는 아님(`lambda.md` Slow cold starts)
- STS: 같은 계정 user를 trust에 직접 지정하면 AWS는 identity policy 불필요, floci는 거부(`t02-iam.log` carol)

## 검증 결과 (2026-11-13, floci 2.4.0 digest 고정)

실행: `lab/s01_function.py`~`lab/s05_async.py`, case `sl1`~`sl5`(`lab/cases.txt`). strict는 `LAB_IAM=true LAB_SIG=true LAB_S3AUTH=true`, 대조는 IAM off. bootstrap은 `test`, 판정 대상 요청은 IAM user `dev`나 Lambda 실행 role. `./verify.sh sl sl`로 9개 case를 두 번 연속 돌려 모두 PASS. 두 round의 차이는 s03의 무작위 표식 값 두 줄뿐이었고, 그 check를 참·거짓으로 바꾼 뒤 `./verify.sh sl3 sl3`에서 32줄이 같았다. 로그: `lab/logs/sl-1/`, `sl-2/`, `sl3-1/`, `sl3-2/`.

### 단계별 판정

| 단계 | 검증 | 결과 | 레슨 제공 |
|---|---|---|---|
| A | W0 | 정상 / 예외(HTTP 200 + `FunctionError: Unhandled`, `errorType: ValueError`) / timeout(`Unhandled`, `Task timed out after 2 seconds`, `Function.TimedOut`) 구분됨. `lambda:InvokeFunction` 없는 user는 strict에서 `AccessDeniedException` | 가능 |
| A | W9 | handler `print`와 예외 traceback은 `/aws/lambda/<fn>`에 남음. 함정 4개(아래 카드 A-1~A-4) | 가능(카드 필수) |
| A' | W10 | 연속 3회 같은 initId·count 1,2,3 / 겹친 3개는 initId 3개, 새 init 2개(warm 1개 재사용) / idle 20초 설정 후 70초 대기하면 새 initId·count 1 / init에 2초 sleep을 넣으면 cold 2.29초·warm 0.01초(sl-1, sl-2는 2.25초·0.01초, floci Docker 수치) | 가능 |
| A' | W11 | provisioned concurrency 1이 `READY`, 그 alias 첫 호출: `initType=provisioned-concurrency`, count 1(provisioning 때 handler 안 돎), init이 호출 약 7초 전에 끝나 있음, 호출 0.01초. 하나를 잡아 둔 채 두 번째 호출은 새 환경으로 넘어가 cold start를 냄(spillover). `$LATEST` 호출은 provisioned 아님 | 가능(카드 A'-1) |
| A' | W12 | REPORT `Init Duration`은 floci가 내지 않음(W9). handler가 찍은 `INIT <id>` 줄 4개 = 환경 4개로 init 횟수 관찰 가능 | initId 방식으로 가능 |
| B | W1 | path parameter·query·header·body·method 전달, Lambda가 준 status(201)·header 그대로. handler 예외 → 502, handler 1회(재시도 없음) | 데이터 경로 가능 |
| B | W1 인가 | 함수 policy(`AddPermission`) 없음, 다른 API의 SourceArn만 있음 → 둘 다 201, handler 호출됨(AWS는 500, handler 미호출). 문자열을 돌려주는 잘못된 proxy 응답 → 200, 빈 body(AWS·floci 문서는 502) | 호출 권한 레슨 불가(카드 B-1, B-2) |
| C | W2 | 같은 handler·table·입력에서 실행 role Allow 없음 → handler 안 `AccessDeniedException`, item 없음 / Allow → OK / Allow+명시 Deny → `AccessDeniedException`. Invoke 자체는 셋 다 성공. handler 신원 `assumed-role/ddb-<k>/put-<k>`. IAM off에서는 셋 다 OK | 가능 |
| D(복습) | W3a | 조건 없는 같은 key 두 번 → 두 번째 값으로 덮어씀 / `attribute_not_exists` → 두 번째 `ConditionalCheckFailedException` / 동시 5개 → 1개 성공, 4개 실패 / PENDING→PAID 조건부 전이 두 번 → `PAID/1` | 가능 |
| D | W8c·D | ESM 성공 함수 main 0/DLQ 0, 실패 함수 handler 3회 뒤 DLQ 1. 쓰기 후 일부러 실패한 메시지: handler 2회, item `PAID/1`, DLQ 0. 같은 orderId 메시지 2개: handler 2회, `PAID/1` | 가능(카드 D-1) |
| E | W8a·b | reserved 1·겹친 3개 → ALLOW 1, `TooManyRequestsException` 2 / 해제 → 3 / async retry 2 → `approximateInvokeCount` 3, retry 0 → 1 | 가능(카드 E-1) |

### 이번에 새로 확인한 floci 차이 (함정 카드)

| 카드 | 문서 또는 AWS | floci 실제 | 판정 |
|---|---|---|---|
| A-1 START/END/REPORT 로그 | `lambda.md:1010` "write their logs, `START`, `END` and `REPORT` included, to the `LogGroup`" | handler 출력만 들어감. 기본 group, `LoggingConfig` 지정 group, `LogFormat=JSON` 모두 같음 | 문서와 다름 |
| A-2 timeout 로그 | AWS는 함수 log stream에 `Task timed out` 줄을 남김 | 함수 로그에는 없고 floci 컨테이너 로그에만 `Function fn timed out after 2s` | AWS와 다름(문서 언급 없음) |
| A-3 로그 조회 권한 | `iam.md:1820` CloudWatch Logs는 floci가 resource ARN을 직접 만든다 | `logs:FilterLogEvents`가 `resource=*`로 평가돼 log-group ARN으로 좁힌 Allow는 거부, `Resource: *`만 허용 | 문서와 다름 |
| A-4 실행 role 로그 권한 | AWS는 실행 role에 `logs:CreateLogGroup`·`CreateLogStream`·`PutLogEvents`가 없으면 로그가 안 남음 | 권한 없는 role의 함수도 로그가 남음 | AWS와 다름(문서 언급 없음) |
| A'-1 init 유형 | AWS는 on-demand 환경에 `AWS_LAMBDA_INITIALIZATION_TYPE=on-demand` | provisioned에만 값, on-demand는 빈 문자열 | AWS와 다름(문서는 provisioned만 언급) |
| B-1 API Gateway → Lambda 호출 권한 | AWS는 함수 policy가 API Gateway를 허용하지 않으면 500 | policy 없음·틀린 SourceArn 모두 201, handler 실행 | AWS와 다름(문서 언급 없음) |
| B-2 잘못된 proxy 응답 | `api-gateway.md:393` "malformed proxy payload … `INTEGRATION_FAILURE`" | 200, 빈 body | 문서와 다름 |
| D-1 ESM 실행 role 권한 | AWS는 실행 role에 queue 소비 권한이 없으면 `CreateEventSourceMapping`을 거부 | 권한 없는 role로 ESM 생성·메시지 소비 모두 됨 | AWS와 다름(문서 언급 없음) |
| E-1 destination 실행 role 권한 | AWS는 OnFailure 대상(SQS)에 보낼 권한이 실행 role에 있어야 전달 | 권한 없어도 레코드 전달 | AWS와 다름(문서 언급 없음) |

정리: 실행 role이 **함수 코드 안에서** 부르는 API(W2의 DynamoDB)는 strict에서 AWS처럼 인가된다. 반면 **Lambda 서비스가 대신 하는 일**(로그 전송, ESM polling, destination 전달)과 **다른 서비스가 Lambda를 부르는 권한**(API Gateway → Lambda)은 floci가 인가하지 않는다. 그래서 권한 레슨은 "함수 코드가 다른 서비스를 부를 때"에 집중하고, 나머지 연결 권한은 카드로 말한다.

### 수업 runner 변경 (V6)

`compose.yml`에 `FLOCI_DOCKER_RESOURCE_NAMESPACE=${LAB_NS:-awslab}`을 넣었다. Lambda·EC2·SG helper 컨테이너가 `floci-aws-awslab-...`, VPC 네트워크가 `floci-aws-awslab-vpc-...`(label `floci_namespace=awslab`)로 만들어지는 것을 확인했다. `run.sh`의 정리는 이 이름·label만 지우도록 바꿨다(전역 `floci-*` 정리 제거). `t05_sg.sh`는 새 이름 규칙으로 고쳤고 `./verify.sh t05ns t05`에서 두 번 같은 결과(16줄)였다. `verify.sh`는 이제 이름을 받아 `logs/<이름>-1`, `-2`에 쓰고 기존 디렉터리가 있으면 멈춘다(baseline `logs/r1`, `r2` 보존).

## 미결 확인사항 (2026-11-13 사용자 지시로 보류)

확장은 아래 검증을 통과하기 전까지 열지 않는다. 기본 단계 수업에는 영향이 없다.

| 항목 | 필요한 확인 | 묶인 확장 |
|---|---|---|
| W3b | 고객별 GSI Query·projection vs base key 조회 | GSI |
| W3c | TTL 만료와 물리 삭제(60초 sweep) 구분 | TTL |
| W4 | SNS queue 2개 fan-out·한 목적지 실패 영향, EventBridge 일치/불일치·없는 target·재시도 실패의 DLQ | EventBridge fan-out |
| W5 | Streams INSERT/MODIFY/REMOVE, 실패 retry·bisect, consumer MODIFY 재진입 방지, S3 ObjectCreated 필터 | Streams형 접수, S3 이벤트 |
| W6 | Step Functions 실제 Lambda task 성공/실패, Retry 횟수·Catch, state machine role Invoke 유/무 | Step Functions |
| W7 | `ReportBatchItemFailures` off/on, batch 3건 중 1건 실패 | partial batch |
| SAM | `AWS::Serverless::Function`과 `Events`가 floci에서 role·permission·ESM을 만드는지 | SAM |
| 실제 AWS 측정 | cold/warm `Init Duration`, 메모리, provisioned 유무 비교. 실제 계정 사용 승인 필요, 과금 근거 확인 전 | cold start 실측 |
| C1 정정 | `capability-matrix.md` "trust policy principal" 행, `topics/02` carol 행의 "AWS와 같음" → "다름" | 권한 심화 확장 |
