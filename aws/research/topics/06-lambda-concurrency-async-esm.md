# 06. Lambda: 동시성 예약, 비동기 호출 실패 처리, SQS event source mapping

## ① 배울 것
Lambda가 managed service로서 대신 해 주는 일(동시 실행 수 제한, 실패한 비동기 호출 재시도, SQS 메시지 재수신과 DLQ 이동)을 429 응답, 재시도 횟수, DLQ 메시지 수로 확인한다.

## ② 왜 MinIO·PostgreSQL 등으로 안 되는가
함수를 컨테이너로 실행하는 것만이면 Docker로 된다. SQS visibility timeout과 재수신은 Redis Streams의 pending/XCLAIM이나 RabbitMQ로도 같은 의미를 배울 수 있다(사용자는 redis·distsys에서 이미 다룸). 그래서 단독 주제로는 뺐다. 이 주제에 남긴 것은 그 위에 AWS가 얹은 계약이다. 함수 단위 reserved concurrency와 계정·리전 풀, `MaximumRetryAttempts`와 OnFailure destination 레코드, ESM이 실패 batch를 queue에 돌려놓아 `RedrivePolicy`가 이어받는 연결이다.

## ③ floci 검증 결과와 판정
실험: `lab/t06_lambda.py` (case `t06-lambda`). 런타임 `python3.12`, 함수 컨테이너는 floci가 Docker socket으로 띄움. 대조는 설정 값을 바꿔 같은 run 안에서 한다. 기대값 출처: [concurrency](https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html), [async destinations](https://docs.aws.amazon.com/lambda/latest/dg/invocation-async-retain-records.html), [SQS error handling](https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-errorhandling.html).

| 확인한 것 | 결과 | 판정 |
|---|---|---|
| reserved concurrency 1, 5초 걸리는 호출 3개 동시 | ALLOW 1, `TooManyRequestsException` 2 | 실험 확인 (`lambda.md:413`) |
| 예약 해제 후 같은 3개 | ALLOW 3 | 실험 확인 (대조) |
| reserved concurrency 0 | `TooManyRequestsException` | 실험 확인 |
| 예약 950 요청 (리전 풀 1000, 최소 100 남겨야 함) | `LimitExceededException` | 실험 확인 |
| 항상 실패하는 함수, `MaximumRetryAttempts=2`, OnFailure SQS | 레코드 `condition=RetriesExhausted`, `approximateInvokeCount=3` | 실험 확인 (`lambda.md:135` "default: 2, total 3 attempts") |
| 같은 함수, `MaximumRetryAttempts=0` | `approximateInvokeCount=1` | 실험 확인 (대조) |
| destination 없이 `DeadLetterConfig` SQS | 본문 = 원래 payload(`id=x1`), `ErrorMessage` 속성에 `boom-on-purpose` | 실험 확인 |
| SQS ESM, 성공하는 함수 | main 0 / DLQ 0 | 실험 확인 |
| SQS ESM, 실패하는 함수 (`VisibilityTimeout=3`, `maxReceiveCount=2`) | main 0 / DLQ 1, 약 9초 뒤 DLQ 도착 | 실험 확인 (`lambda.md:1246`) |

## ④ floci에서 깨지거나 주의가 필요한 부분
- 재시도 간격은 실험용으로 `FLOCI_SERVICES_LAMBDA_ASYNC_RETRY_DELAY_SECONDS=0`로 줄였다. AWS는 1분, 2분을 기다린다(`lambda.md` 원문 "the first retry waits one minute and the second two"). 레슨에서 이 차이를 밝힌다.
- ESM의 `ScalingConfig.MaximumConcurrency`는 저장만 한다. 원문(`lambda.md:1312`): "the poller today serializes invocations per ESM to one at a time regardless". ESM 동시성 레슨은 하지 않는다(실험하지 않음, 문서 기준).
- concurrency가 찬 상태에서 비동기 재시도는 1초마다 다시 시도한다(AWS는 최대 5분까지 back off). 문서 기준이고 실험하지 않았다(확인 못 함).
- S3 OnFailure destination은 전달되지 않는다(`lambda.md` "**An S3 `OnFailure` destination is not delivered.**"). 실험하지 않았다.
- Lambda 실행 role은 저장만 하고, 함수 안 코드가 그 role로 서명하는지는 시험하지 않았다(확인 못 함).

## ⑤ 실습 스크립트
- `aws/research/lab/t06_lambda.py` — 실행: `./run.sh t06` (첫 실행은 Lambda 런타임 이미지 pull로 수 분 걸림)

## ⑥ 예상 레슨 수와 순서 (3)
1. reserved concurrency: 예약 1에서 429가 나오는 장면, 예약 0 = 함수 정지 스위치
2. 비동기 호출: 재시도 횟수와 OnFailure 레코드(`approximateInvokeCount`), DLQ와의 차이
3. SQS ESM: 실패 → visibility timeout 뒤 재수신 → `maxReceiveCount` 뒤 DLQ, 성공 함수와 대조
