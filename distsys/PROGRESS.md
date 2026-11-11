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
| ⑥ | (심화) 순서 | ✅ | 두 릴레이·SKIP LOCKED로 v2→v1 발행 역전 재현. 소비자 `if n and ev["version"] > latest:`로 수정(사용자 지시 없이 튜터가 적용). `6-reordered` 결제 0건·v2/cancelled, 전체 14개 시나리오 기대값 일치 (2026-11-10) |
| ⑦ | (심화) 컨슈머 그룹 | ✅ (2026-11-11 사용자 설명 수락) | 관찰 미션. `m7_group.py`·`m7_payment_service.py`·시나리오 `7-rebalance` 실행 확인(2026-11-11): P0·P1, A·B, A가 DB 커밋 직후 사망 → B가 P0 재수신·inbox skip, 결제 2건. 전체 15개 일치. 사용자 설명 대기 |

상태: ⬜ 안 함 · 🔄 진행 중 · ✅ 완료

## 약점
- 2026-11-07 설명 방식 교정: "위치 2개"의 소유자와 관리 단위를 생략한 설명 때문에 P0 공용 위치로 오해가 생김. A·X의 현재/커밋 위치 총 4개를 단계별로 추적하는 텍스트 그림·상태표가 효과적이었음. 재발 방지 절차는 `AGENTS.md`의 "Kafka 설명 방식" 참고. 사용자 요청으로 기록했으며 회고 통과 기록은 아님.
- Kafka 용어(topic/key/value/partition/offset)와 업무 필드(order_id/event_id)를 명확히 구분해서 설명할 것.
- 설명에는 누가 어느 DB/브로커에 무엇을 하는지 주어와 목적지를 포함할 것. 코드에는 한국어 주석 필수.

## 다음 단계
### 다음 세션 재개 순서 (2026-11-11 저장)
1. ①~⑦은 모두 ✅. 사용자가 범위 밖 주제 중 **CDC 비교 데모부터** 하기로 골랐다(사가 오케스트레이터는 그다음 후보, 멱등 키는 별도 데모 없이 생략).
2. CDC는 아직 코드·설정을 만들지 않았다. 합의한 계획은 **A 방식(가벼운 버전)**: `compose.yaml`의 postgres에 `wal_level=logical`만 추가하고(변경 후 컨테이너 재생성 필요), `test_decoding` + `pg_logical_slot_peek_changes` / `get_changes`로 WAL을 SQL로 읽는다. 확인할 4가지: ① 커밋된 변경만 나옴(ROLLBACK은 안 나옴) ② `peek`는 위치 유지, `get`은 위치 이동(Kafka 현재·커밋 위치와 대응) ③ LSN ④ 읽는 쪽이 없으면 slot이 WAL을 붙잡음(`pg_replication_slots`). 출력 형태는 실행 전이라 확인 못 함.
3. A로 못 보는 것(Debezium 커넥터 → Kafka 전송, 설정·스냅샷·스키마 변경, 커넥터 복구·중복)은 필요하면 B(Kafka Connect + Debezium 컨테이너 추가)로 이어 간다. B는 이미지가 크고 설정 지점이 많다고 추정함(확인 못 함).
4. 시작할 때 `AGENTS.md` 미션 표에 ⑧ CDC 한 줄을 추가하고, `run.py`에 시나리오(`8-...`)를 넣는다. 기대값은 "미션을 끝낸 뒤의 결과". 코드는 시작할 때 만든다.
5. 환경: OrbStack이 꺼져 있으면 `open -a OrbStack` 후 `cd distsys/lab && docker compose up -d --wait`(Windows는 Docker Desktop). 재현은 `uv run run.py <시나리오>`, 회귀는 `uv run run.py all`(15개).

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

## 2026-11-10 ⑥ 순서 (실행 확인 + 설명)
- 실행 확인: 수정 후 `6-reordered` 결제 0건, 소비자 상태 v2/cancelled. `uv run run.py all` 14개 기대값 일치(❌ 줄은 ①·② 관찰 시나리오의 의도된 결과).
- 사용자가 이해한 것: 순서 역전 현상, inbox는 event_id 중복만 막음, 오래된 version은 업무 SQL 생략, 건너뛰어도 inbox 기록·오프셋 커밋은 함, 이벤트가 변경 후 값이어야 version 건너뛰기가 안전함(+3/+5 변경분은 건너뛰면 틀림). 이 항목들은 반복 설명하지 않는다.
- 사용자가 제기한 한계(설명만): 이벤트 종류가 늘면 version 한 줄로 부족. 실무 방향은 ① 변경 후 값 이벤트 ② 릴레이에서 같은 주문 순서 발행(`NOT EXISTS` 앞선 미발행 이벤트, 또는 order_id 해시로 워커 고정) ③ 소비자 version 검사. 순서가 중요한 변경분용 대기 표 방식은 실무에서 드물어 구현하지 않음.
- 스키마 메모: 현재 `outbox`는 `order_id`·`version`이 `payload` jsonb 안에 있음. 릴레이 쿼리를 쓰려면 컬럼으로 빼는 편이 낫지만 실습에서는 바꾸지 않음.
- 세션 운영 기록: 추상 설명과 되묻기를 반복해 사용자가 여러 번 이해 못 했다고 함. 루트 `AGENTS.md`에 "이해 못 함 규칙" 추가(사용자 요청). 다음 세션 재개는 ⑦부터.
- 다음: ⑦ 컨슈머 그룹(파티션 2개+, 결제 소비자 2개). 코드는 시작할 때 만든다.

## 2026-11-10 회고
- 회고 pass

## 2026-11-11 ⑦ 컨슈머 그룹 (실행 확인 + 설명)
- 실행 확인: `uv run run.py 7-rebalance` 결제 누락·중복·유령 0, `run.py all` 15개 기대값 일치. 사용자가 직접 고친 코드는 없다(관찰 미션).
- 관련 코드
  - `lab/m7_payment_service.py`: 같은 그룹 `payment`의 consumer 1명(NAME=A/B). inbox INSERT와 결제 INSERT를 한 트랜잭션 → `crash_point("after_db")` → 오프셋 커밋. 파티션 할당·반납과 수신을 로그로 남김.
  - `lab/m7_group.py`: 실행기. topic을 2파티션으로 재생성 → A(`CRASH_AT=after_db`)·B 시작 → 각자 파티션 1개씩 받을 때까지 대기(sleep 없음) → P0·P1에 1건씩 발행 → A 사망 대기 → B의 `skip dup` 로그 대기 → B 종료.
  - `lab/run.py`: `SCENARIOS["7-rebalance"]` 추가, 기대값은 누락·중복·유령 0.
- 실제 로그 시간순 (E1=757fd25a P0, E2=64cda6c8 P1)
  1. `A assigned [0]`, `B assigned [1]`. DB 비어 있음, 커밋 위치 없음.
  2. 실행기가 P0 offset0=E1, P1 offset0=E2 발행. A가 E1, B가 E2 수신.
  3. A: DB 커밋(processed_events E1 + payments E1) 직후 💥 사망. Kafka P0 커밋 위치는 0 그대로. A 메모리의 현재 위치는 소멸.
  4. B: E2 DB 커밋 → 오프셋 커밋(P1 커밋 위치 1), `paid`.
  5. 리밸런스: `B revoked [1]` → `B assigned [0, 1]`. 멤버가 B 하나라 할당 정책과 무관하게 B가 전부 맡음.
  6. B가 P0를 커밋 위치 0부터 읽어 E1 재수신. inbox INSERT 0행 → 결제 생략 → 오프셋 커밋(P0=1), `skip dup`.
  7. 최종: E1 수신 2번(A 1, B 1), 결제 INSERT 1번, 결제 2건.
- 확인한 것 / 못 한 것: 위 로그는 실행 확인. 사망부터 리밸런스까지 걸린 시간(`session.timeout.ms=6000` 설정)은 로그에 시간이 없어 확인 못 함. 기본 할당 정책 이름(`range,roundrobin`)은 기억이며 이번 실행으로 가리지 않음. B가 P1을 반납했다 다시 받는 단계는 로그로 확인(앞선 설명엔 생략했던 장면, 결과는 동일).
- 이번 세션 설명 실패 기록(사용자 요청으로 남김): 처음 예측 질문에서 리밸런스 설명·전제(DB 상태, inbox 내용, 누가 몇 건 처리했는지)를 빼고 결과를 물어 항의를 받음. 이후에도 설명 뒤에 같은 질문을 다시 던져 "이해 못 함 규칙"을 어김. 규칙 보강: 루트 `AGENTS.md`에 트리거 확대(항의·욕설), "사용자 질문에 답하고 내 질문을 반복하지 않는다", "표현 정확도" 절 추가, `distsys/AGENTS.md`의 "첫 예측 질문 5분 안" 삭제.
- 사용자가 이해한 것으로 기록하지 않는다: ⑦의 이유 한 줄 설명은 아직 받지 않음.

## 2026-11-11 ⑦ 이어서 (설명만)
- 그룹 구조 정리: `7-rebalance`는 그룹 `payment` 하나에 A·B가 있다. 리밸런스는 같은 그룹 안에서만 일어난다. 다른 그룹은 같은 P0를 따로 읽고 커밋 위치도 따로 가지며, 서로의 담당자를 바꾸지 않는다. 같은 그룹 안에서 P0는 한 시점에 consumer 한 명만 맡는다. 사용자가 이 세 가지를 스스로 정확히 말함.
- 위치 소유자 정리: Kafka는 그룹별 커밋 위치만 저장하고, 현재 위치는 consumer 메모리에만 있다. `poll`은 현재 위치부터 요청하며 Kafka 저장값을 바꾸지 않는다. 사용자가 "Kafka가 위치 2개를 관리한다"고 이해했던 부분을 위 구분으로 교정. 사용자가 "이해한 것 같다"고 함(확인 질문은 받지 않음).
- 코드 위치 안내: `m7_payment_service.py`의 `on_assign`(20)·`on_revoke`(26)·`subscribe`(33), `common.py:54` `session.timeout.ms`. 리밸런스 자체는 라이브러리·브로커가 처리.
- ⑦ 설명 수락: 사용자가 대화 중 직접 "A가 inbox·결제를 DB에 커밋했지만 offset 커밋이 Kafka에 반영되지 않았고, B가 P0를 맡아 E1을 다시 받지만 inbox INSERT가 0행이라 추가 결제 없이 offset을 커밋한다"고 설명함. 보충 한 가지: A는 offset 커밋을 보내다 죽은 게 아니라 DB 커밋 직후 `after_db`에서 죽어 커밋 코드가 실행되지 않음(결과 동일). 별도의 한 줄 문장은 요구하지 않고 ✅ 처리.
- 재시작 시 흐름 이해(설명만): 다시 시작한 consumer는 그룹의 커밋 위치를 Kafka에서 읽어 현재 위치로 삼는다. 저장된 커밋이 없으면 `auto.offset.reset`.
