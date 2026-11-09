# 분산 이벤트 패턴 진행 현황 (튜터가 미션·질문마다 갱신)

튜터 규칙과 미션 표는 [AGENTS.md](AGENTS.md)에 있습니다.

## 복습 문서
- [Kafka offset의 단계별 위치 변화](notes/kafka-offset.md): 두 그룹 A·X의 현재 위치와 커밋 위치, 장애·재시작·inbox 처리 시나리오. 개념 설명 자료이며 두 그룹 실행 로그는 아님.

## 프로필
- 계기: YouTube "The Outbox Pattern" (2026-11-02). 빠르게 배우고 실제로 실습하기를 원함.
- 범위 요청: outbox, inbox, CQRS, 가능하면 분산 환경. 보상 트랜잭션·순서 보장도 넣자고 함 → 심화 ⑤~⑦.
- 결정 (2026-11-02): DB는 Postgres, 언어는 Python + uv, 도메인은 주문 → 결제, ORM 없이 raw SQL, 시나리오마다 한 명령으로 확인·재현.
- 다른 언어 경험: Python·Java·C++(알고리즘), TypeScript(React). SSAFY 교육생.
- 선호: 세션당 20~30분, 대화로 한 문제씩, 쉬운 건 빠르게. "이걸 쓸 일이 있나?"를 자주 물음.
- 아는 것: 사가 = 보상 트랜잭션으로 알고 있었음 → 사가는 로컬 트랜잭션 여러 개의 흐름이고 보상 트랜잭션은 그중 되돌리기 부분이라고 설명함 (2026-11-02, 설명만).

## 미션
| # | 미션 | 상태 | 메모 |
|---|---|---|---|
| 0 | 환경 준비 | ✅ | 튜터가 준비. 이미지 pull, `up --wait`, `run.py all` 통과 확인 (2026-11-03) |
| ① | 이중 쓰기 | ✅ | 코드 준비됨: `m1_order_service.py`, `m1_payment_service.py`. 시나리오 `1-ok`, `1-db-first`(결제 누락 1), `1-publish-first`(유령 결제 1). 튜터가 실행해 확인 |
| ② | outbox + 폴링 릴레이 | ✅ | 주문/outbox 원자성 수정, 발행 후 sent 갱신 전 장애의 중복 확인. 전체 6개 시나리오 기대값 통과 |
| ③ | inbox (③-a 트랜잭션, ③-b 오프셋) | ✅ | inbox·결제 원자성, 자동 오프셋 커밋 해제, DB 커밋 뒤 명시적 오프셋 커밋 구현. 중복도 DB 트랜잭션 종료 후 커밋. `3-offset-auto` 누락 1→0 실행 확인 (2026-11-07) |
| ④ | CQRS 프로젝션·재생 | ✅ | 조회 전용 inbox로 분리. 중복 전달 시 합계 중복 없음, 새 그룹으로 조회 모델 재구축 확인. 전체 11개 시나리오 기대값 일치 (2026-11-07) |
| ⑤ | (심화) 보상 트랜잭션 | ✅ | 주문 inbox·취소 UPDATE 원자성 수정. 취소 전 장애 복구·실패 이벤트 중복 전달 검증. 전체 13개 시나리오 기대값 일치 (2026-11-07) |
| ⑥ | (심화) 순서 | 🔄 | 두 릴레이·SKIP LOCKED로 v2→v1 발행 역전 재현. `6-reordered` 수정 전 취소된 주문 결제1 확인. 소비자의 업무 버전 검사가 결정 지점 |
| ⑦ | (심화) 컨슈머 그룹 | ⬜ | |

상태: ⬜ 안 함 · 🔄 진행 중 · ✅ 완료

## 약점
- 2026-11-07 설명 방식 교정: "위치 2개"의 소유자와 관리 단위를 생략한 설명 때문에 P0 공용 위치로 오해가 생김. A·X의 현재/커밋 위치 총 4개를 단계별로 추적하는 텍스트 그림·상태표가 효과적이었음. 재발 방지 절차는 `AGENTS.md`의 "Kafka 설명 방식" 참고. 사용자 요청으로 기록했으며 회고 통과 기록은 아님.
- Kafka 용어(topic/key/value/partition/offset)와 업무 필드(order_id/event_id)를 명확히 구분해서 설명할 것.
- 설명에는 누가 어느 DB/브로커에 무엇을 하는지 주어와 목적지를 포함할 것. 코드에는 한국어 주석 필수.

## 다음 단계
### 다음 세션 재개 순서 (2026-11-09 저장)
1. **⑥ 순서 역전부터 바로 재개한다.** ①~⑤ 설명·확인 질문은 반복하지 않는다. 직전 예측 질문은 제시만 했고 사용자의 답변은 아직 받지 않았다.
2. 환경을 띄운 뒤 다음 텍스트 그림으로 상황을 다시 제시한다.
   ```text
   업무 발생: 생성 v1(E1) → 취소 v2(E2)
   릴레이 A: v1 행 잠금 후 지연
   릴레이 B: SKIP LOCKED로 v2 먼저 발행
   Kafka P0: offset 0 = 취소 v2, offset 1 = 생성 v1
   ```
3. 이어 물을 질문: "취소 v2를 반영한 뒤 생성 v1을 받았다. E1과 E2는 다른 event_id인데 inbox만으로 막을 수 있나? 이미 반영한 version과 무엇을 비교해야 하나?" 사용자의 답을 먼저 받는다.
4. 확인할 파일은 `lab/m6_payment_service.py`. 수정 지점은 `latest` 조회 다음의 `if n:`이다. 사용자의 수정 방향을 받은 뒤 버전 검사를 추가한다. 아직 수정하지 않았다.
5. `cd distsys/lab` 기준 `uv run run.py 6-reordered` 재실행 → 결제 0건·소비자 상태 v2/cancelled 확인 → `uv run run.py all`. ⑥ 추가 이후 전체 회귀는 아직 실행하지 않았고, 직전 전체 통과는 ①~⑤의 13개 시나리오다.

튜터 사전 실행 결과: `6-reordered`에서 원본 cancelled인데 소비자 상태 v1/paid, 결제 1건으로 빨강 확인. 다음 세션에 이를 사용자 이해 완료로 취급하지 않는다. 이번 저장 요청은 회고가 아니며 회고 결론을 대신 작성하지 않는다.

### 구현 맥락
⑥ 진행 중. `lab/m6_payment_service.py`의 `if n:`을 업무 version까지 비교하도록 수정하는 결정 지점이 남음. `latest`는 해당 주문에서 소비자가 이미 반영한 최신 version. 현재 inbox만 검사하므로 별도 event_id의 오래된 생성도 적용함. `6-reordered` 수정 전 빨강 실행 확인. 사용자가 예측·수정 방향을 말하면 수정 후 같은 시나리오와 전체 회귀 검증. business version과 Kafka offset을 구별할 것. 이번 시나리오는 취소를 먼저 본 후 늦은 생성을 막는 경우이며, 이미 성공한 결제의 환불이나 모든 종류의 이벤트를 안전하게 건너뛰는 일반 해법까지 검증하는 것은 아님.
세션 시작 시 OrbStack이 꺼져 있으면 `open -a OrbStack` 후 `docker compose up -d --wait`.

## 2026-11-03 학습
- ① 첫 예측: 주문 DB 커밋 후 발행 전 죽으면 주문은 남고 결제는 누락된다고 스스로 설명함(설명만). Docker 이미지 다운로드 중으로 실행 확인 대기.

- 추가 대화(설명만): 사용자는 기존 구현에서 주기적 DB 조회와 행 잠금으로 발행하는 워커를 사용했다고 함. 폴링 릴레이의 배치 위치(앱 내부/별도 프로세스)와 CDC 방식의 차이를 설명. outbox는 누락 방지, 중복 가능성은 남는다고 설명.
- 추가 질문(설명만): CDC는 Kafka 필수가 아님. Debezium의 Kafka Connect 배치와 Server의 다양한 sink를 구분하고, 브로커별 대표 용도를 설명.
- 추가 질문(설명만): CDC 릴레이도 브로커 전송 실패 가능함을 사용자가 지적. Debezium은 WAL 위치/오프셋으로 복구하며 중복 가능, replication slot과 WAL 보존 관리가 필요하다고 설명.
- 추가 질문(설명만): 전송 성공 후 오프셋 저장 실패는 재전달/중복으로 이어짐. PostgreSQL WAL→logical decoding→Debezium→Kafka 흐름, 소스 LSN과 Kafka 소비 오프셋 구분. PostgreSQL 커넥터는 단일 task이며 샤드/DB별 분리와 하류 소비자 확장을 구분해 설명.
- ① 1-db-first 실행 확인: 주문 3건, 결제된 주문 2건, 결제 누락 1/중복 0/유령 0. 사용자 예측과 일치. Windows cp949 출력 오류는 PYTHONUTF8=1로 재실행해 정상 장애 훅과 결과 확인. 다음: 발행 먼저 하고 DB 저장 전 죽는 경우 예측.
- 학습 방식 요청: 코드를 읽을 때 함수 역할과 실행 순서를 알 수 있도록 한국어 주석 필요. m1_order_service.py에 DB 커밋, 장애 훅, Kafka 발행 인자·응답 대기 설명 추가(주석만 변경).

- ① 완료: 사용자가 순서를 바꿔도 두 작업 사이 장애가 문제라고 설명. 1-publish-first 실행 확인: 주문 2건/결제된 주문 3건/유령 결제 1. 앞선 결제 누락과 비교 완료. 다음 미션은 ② outbox + 폴링 릴레이.
- ② 시작: m2_order_service.py(境界 수정용), m2_relay.py와 2-atomic/2-after-db/2-duplicate 시나리오 준비. 튜터가 2-atomic 실행해 수정 전 결제 누락 1 및 기대 불일치 확인. 사용자에게 두 INSERT 사이 장애 예측 요청 중. 아직 수정/전체 회귀 전.
- ② 사용자 지시로 두 INSERT를 같은 transaction 블록으로 수정. 2-atomic 재실행: 주문/결제 0건, 누락 0 확인. 전체 시나리오에서 2-after-db 주문1/결제1, 2-duplicate 중복1 관찰. 원자성 수정 이유는 사용자가 설명 완료. 다음: 릴레이 발행 후 sent 기록 전 장애의 중복 원인 질문.
- ② 중복 원인: 사용자가 발행 성공 후 sent 갱신 실패/롤백으로 재발행됨을 설명. 재시작 후 재전달이며 현재 예외 처리 없는 코드는 즉시 다음 while이 아닌 종료임을 보충. event_id가 이미 멱등 키 역할, 브로커 producer idempotence와 소비자 inbox의 범위 차이를 설명. 다음 ③ inbox.
- 추가 질문(설명만): 사용자가 반복 장애→반복 발행, 파티션 할당과 소비자 poll, 소비자 중복 방지 구조를 연결함. order_id 기반 결제 UNIQUE(업무 중복 방지)와 event_id 기반 inbox(이벤트 중복 방지)를 구분해 설명. 다음: inbox 실습 진행.

- 세션 종료 요청: inbox부터 다시 학습할 수 있도록 커밋. inbox는 설명만 했고 아직 구현/검증하지 않음. 처리 기록과 결제를 함께 커밋하는 단순 inbox와 별도 워커/상태 관리 구조를 구분해 설명함. run.py all의 6개 시나리오 통과 확인 완료.

- 2026-11-03 ③-a 시작: 사용자가 ㉠+㉡ 분리 시 누락, 한 트랜잭션이면 재전달 때 둘 다 재실행됨을 설명. 죽은 컨슈머가 그룹에 남아 다음 poll이 비는 문제는 session.timeout.ms=6000, reset의 그룹 삭제 재시도, m3 IDLE=10으로 해결. run.py all: 3-inbox-crash만 ❌(정상, 고치기 전).
- ③-a 수정: 사용자 지시로 튜터가 ㉠㉡을 `with conn.transaction()`으로 묶음. 3-inbox-crash 빨강→초록, run.py all 8개 통과(확인). 남음: 사용자의 '왜 막히는지' 한 줄 설명, ③-b 오프셋.
- ③-b 준비: 자동 오프셋 커밋(5초 백그라운드, 라이브러리 스레드)이 DB 처리 성공과 무관함을 실험으로 확인(poll 후 7초 뒤 kill해도 오프셋 커밋됨). 사용자가 '읽었음 먼저 나가면 inbox도 못 막아 누락'을 설명(설명만). `m3b_payment_service.py`(SLOW 지연 추가, 자동 커밋 켜짐)와 시나리오 `3-offset-auto` 준비: 고치기 전 누락 1(빨강)을 실행해 확인. 남음: 사용자가 자동 커밋 끄고 DB 커밋 뒤 commit 추가. ③-a '이미 커밋된 이벤트 재전달 시 ㉠ 0행→건너뜀' 답은 아직 못 받음(3-inbox-dup 실행으로는 확인).

## 2026-11-03~04 ③-b 개념 정리 (설명만, 사용자가 이해한 것)
- 오프셋 자동 커밋은 라이브러리 기본값(`enable.auto.commit=true`)이고 우리 코드가 보낸 게 아님. 백그라운드 스레드가 ~5초마다 poll한 위치를 커밋. `crash_point`는 우리 Python 프로세스만 죽임(Redpanda·Postgres는 그대로). 그래서 5초 전에 죽으면 재전달되고(③-a가 통과한 이유), 5초 후 죽으면 누락.
- inbox는 중복을 막고, 오프셋 타이밍은 누락과 관련됨. outbox 릴레이의 `sent`(성공 응답 뒤에 표시)와 같은 규칙: 컨슈머는 DB 커밋 뒤에 오프셋 커밋.
- 프로듀서: `produce()`는 큐에 넣기만(배치 전송), `common.py publish()`의 `flush()`가 응답까지 대기하는 동기 방식. 비동기는 콜백에서만 `sent` 갱신. 대규모는 배치+워커+CDC. 실습은 동기.
- outbox 구조 재정리: INSERT(orders+outbox)는 주문 서비스, SELECT→publish→UPDATE는 릴레이. 발행 성공 후 UPDATE 실패면 Kafka엔 들어갔고 DB는 롤백 → 중복, inbox가 막음.
- m3b는 별도 워커 없는 단순 inbox(한 루프가 poll→트랜잭션→오프셋 커밋). 별도 워커 구조는 inbox 저장 커밋 뒤 오프셋 커밋.

## 2026-11-07 ③-b 이어서
- 수정 전 `3-offset-auto` 재실행: 주문 1건/결제 0건/누락 1건, 기대 불일치 확인.
- 복습 답변(설명만): 사용자가 DB 커밋 뒤 오프셋 커밋 전 장애 시 재전달되고, inbox의 기존 event_id 때문에 INSERT 0행 → 건너뛰어 이중 결제를 막는다고 설명함. Kafka에는 이벤트가 남아 있고 소비자 그룹의 커밋 위치가 갱신되지 않은 것이라고 용어 보충.
- Kafka 개념 복습(설명만): partition별 offset 독립, consumer group 내 개별 consumer에 partition 할당(한 consumer가 여러 partition 가능), 그룹·topic·partition별 커밋 위치를 설명. 사용자가 중복 이벤트도 오프셋 커밋해야 재전달을 피한다고 답함. 보충: 살아 있는 consumer의 다음 poll은 현재 위치로 진행하며, 커밋은 재시작·재할당 시 시작 위치를 보존한다. 코드 수정은 아직 하지 않음.
- ③-b 사용자 설명: Kafka 오프셋 커밋은 DB 트랜잭션으로 롤백되지 않으므로 with 밖에 둬야 한다고 지적. DB 커밋 후 Kafka 커밋 미반영 장애에서는 재수신·inbox 중복 확인·커밋한다고 설명함(설명만). Kafka 커밋 성공 후 장애와 미반영 장애를 구분해 보충함.
- 사용자 지시로 `m3b_payment_service.py` 수정: 자동 오프셋 커밋 해제, 신규/중복 모두 DB 트랜잭션 정상 종료 후 공통 위치에서 동기 오프셋 커밋. 짧은 한국어 주석 추가. `3-offset-auto` 재실행: 주문 1건/결제 1건, 누락·중복·유령 0(확인).
- 수정 후 `uv run run.py all` 전체 9개 시나리오 기대값 일치 확인. ①·② 관찰 시나리오의 의도된 누락·중복·유령도 기대값대로 재현됨. 실무 연결: 결제 consumer에서 DB 처리 완료와 Kafka 소비 위치 저장 사이의 장애를 다루는 방식.
- ④ 개념 도입(설명만): 사용자가 조회 consumer는 결제와 별도 그룹이어야 한다고 설명. 이미 이해한 그룹 독립성의 당연한 확인 질문을 반복하지 말라고 요청함. projection은 화면용 파생 데이터를 저장하는 작업이고 CQRS 자체가 별도 테이블을 필수로 요구하지 않음을 설명. 사용자가 데이터 중복 비용, 원본 추가 시 조회 모델 갱신 필요성, 집계 조회의 효용을 지적함. 아직 ④ 구현·실행 전.
- ④ 추가 질문(설명만): customer_totals는 고객별 1행의 파생 집계 테이블임을 확인. column-oriented DB의 대량 집계 최적화와 projection의 사전 계산을 구분해 설명하며, ClickHouse처럼 두 방식을 함께 사용할 수 있음을 공식 문서로 확인. ④ 구현은 아직 전.
- ④ CQRS 개념(설명만): 사용자가 조회/변경 분리와 조회 응답시간 개선 목적을 정리. 대규모 시스템에만 필요한지, CDC도 이벤트 기반 아닌지 질문. 이벤트 기반이라는 상위 방식 아래 outbox의 polling/CDC 릴레이를 구분하고, 업무 테이블 직접 CDC와 outbox CDC의 이벤트 의미 차이를 설명함. Debezium 공식 Outbox Event Router 문서 확인.
- CDC 롤백 경계 보충(설명만): 사용자가 orders/order_items 직접 CDC 시 롤백과 outbox의 최종 커밋 여부를 질문. PostgreSQL+Debezium은 직접 테이블 CDC도 커밋된 변경을 전달하므로, outbox가 롤백 안전성을 새로 제공하는 것은 아님. orders·order_items·outbox는 하나의 트랜잭션으로 함께 커밋되며 outbox의 별도 최종 커밋이 아님. outbox의 추가 가치는 명시적인 업무 이벤트·payload 계약이라고 구분. Debezium PostgreSQL 공식 문서 확인.
- ④ 실습 준비·사전 검증: 결제 후 projection이 같은 processed_events를 쓰는 상태에서 `4-projection-dup` 실행. 주문1/결제1, 조회 주문0/고객 합계 없음, projection_errors=2로 수정 전 빨강 확인. Kafka 그룹은 별도라도 DB inbox를 공유하면 조회 작업을 건너뛴다는 결정 지점 질문 예정. 조회 전용 inbox 테이블과 재생 스크립트는 준비했지만 아직 연결 수정·재생 검증·전체 회귀 전. git diff --check 통과.
- ④ 사용자 답변: 처리 역할별 inbox 테이블 분리 또는 구분 컬럼 사용을 제안하고, 공유하면 먼저 처리한 쪽의 기록 때문에 다른 쪽 INSERT 0행→업무 처리 생략임을 설명함. 튜터가 조회 전용 projection_processed_events로 수정(1줄과 주석).
- 수정 후 확인: `4-projection-dup` 주문1/결제1/조회1/kim 합계10000, 중복 이벤트 두 번째는 projection skip. `4-replay` 조회 테이블·조회 inbox만 비운 뒤 새 그룹으로 topic 재생, 주문2/결제2/조회2/kim 합계20000 확인. topic·원본·결제 이력은 재생 도중 유지. 전체 회귀 실행 중.
- ④ 전체 회귀 완료: `uv run run.py all` 11개 시나리오 기대값 일치(확인). inbox의 처리 주체는 개별 consumer 인스턴스가 아니라 결제/조회 같은 처리 역할임을 보충함. 동일 역할의 복제 consumer들은 같은 inbox를 공유한다. 실무 연결: 조회 로직 수정 후 topic 재생으로 읽기 모델을 복원할 때 사용.
- ⑤ 시작: 주문의 status(created/cancelled), payments DB의 payment_failures·payment_outbox, orders DB의 order_processed_events 준비. 결제 실패 이벤트는 payment-results topic으로 반대 방향 전달. 실제 PG는 없고 항상 잔액 부족으로 실패시키는 실습. `5-cancel-crash` 사전 실행 확인: 주문 inbox 커밋 뒤 취소 전 장애 → 재시작 skip → 주문 created 유지, 결제 실패1/실제 결제0, 보상 불일치1(수정 전 빨강). `5-failure-dup` 시나리오도 추가했으나 아직 실행 전. git diff --check 통과.
- ⑤ 개념 설명(설명만): 사용자가 외부 서비스에 걸친 처리를 반대 방향 이벤트로 되돌리는 구조와 Git revert 비유를 연결. 같은 DB라도 이미 커밋한 트랜잭션은 ROLLBACK 불가, 별도 DB의 로컬 트랜잭션을 하나로 묶을 수 없는 경계가 핵심임을 보충. PaymentFailed는 성공한 결제의 취소 이벤트와 구분함.
- ⑤ 사용자 지시: 주문 inbox와 실제 주문 상태 변경을 같은 트랜잭션으로 묶도록 설명함. 튜터가 m5_order_consumer.py 수정, before_cancel 장애 훅은 두 SQL 사이에 유지. `5-cancel-crash` 재시작 후 cancel apply·cancelled·보상 불일치0 확인. `5-failure-dup` 결제 실패 DB 커밋 후 장애/릴레이 발행 후 장애를 복구하고 cancel apply→skip, cancelled·실제 결제0 확인. 전체 회귀 실행 중. git diff --check 통과.
- ⑤ 전체 회귀 완료: `uv run run.py all` 13개 시나리오 기대값 일치(실행 확인). 사용자가 inbox·주문 취소 원자성의 필요성을 설명했고 해당 경계를 수정해 장애 복구 성공. 실무 연결: 실패 이벤트 처리 기록과 보상 UPDATE를 함께 커밋해 재시도 때 보상을 빠뜨리지 않도록 한다. 실제 PG 환불·보상 타임아웃·재시도 운영은 범위 밖이며 이번에는 가짜 결제 실패→주문 취소만 검증.
- ⑥ 준비·사전 실행(확인): m6_seed.py가 같은 주문의 생성 v1·취소 v2를 순서대로 커밋. m6_relay.py의 두 worker가 각각 DB 연결·Producer를 사용하며 Event로 동기화(sleep 없음). A가 v1 잠근 동안 B가 SKIP LOCKED로 v2를 먼저 발행, 이후 A가 v1 발행. 같은 key·같은 partition에서 offset0=취소v2, offset1=생성v1 확인. 서로 다른 event_id라 inbox만으로 막지 못해 원본 cancelled/소비자 paid v1/결제1로 기대 불일치. version 검사 수정 전이며 전체 회귀 미실행. git diff --check 통과.

## 2026-11-10 회고
- 회고 pass
