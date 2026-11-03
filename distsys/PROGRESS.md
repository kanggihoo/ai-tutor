# 분산 이벤트 패턴 진행 현황 (튜터가 미션·질문마다 갱신)

튜터 규칙과 미션 표는 [AGENTS.md](AGENTS.md)에 있습니다.

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
| ③ | inbox (③-a 트랜잭션, ③-b 오프셋) | 🔄 ③-a ✅(코드·시나리오), ③-b 수정 대기 | ③-a 코드 준비: `m3_payment_service.py`(㉠㉡ 분리 상태), 시나리오 `3-inbox-crash`(고치기 전 누락 1이 정상), `3-inbox-dup`(통과). 사용자는 ㉠㉡ 한 트랜잭션 필요성을 설명함(설명만) |
| ④ | CQRS 프로젝션·재생 | ⬜ | |
| ⑤ | (심화) 보상 트랜잭션 | ⬜ | |
| ⑥ | (심화) 순서 | ⬜ | |
| ⑦ | (심화) 컨슈머 그룹 | ⬜ | |

상태: ⬜ 안 함 · 🔄 진행 중 · ✅ 완료

## 약점
- Kafka 용어(topic/key/value/partition/offset)와 업무 필드(order_id/event_id)를 명확히 구분해서 설명할 것.
- 설명에는 누가 어느 DB/브로커에 무엇을 하는지 주어와 목적지를 포함할 것. 코드에는 한국어 주석 필수.

## 다음 단계
③-b 수정부터 이어서. `lab/m3b_payment_service.py`를 고친다 (고치기 전 `uv run run.py 3-offset-auto`는 결제 누락 1, 빨강이 정상):
1. 18줄 `consumer("payment", **{"enable.auto.commit": False})`로 자동 커밋 끄기
2. `with conn.transaction():` 블록이 끝난 뒤, `print("paid ...")` 앞에 `c.commit(message=msg, asynchronous=False)`
3. 중복(`n == 0`)으로 `continue`하기 직전에도 `c.commit(...)` (안 하면 재시작마다 같은 중복을 다시 받음)
고친 뒤 `3-offset-auto` 초록, `run.py all` 전체 통과 확인 → 사용자가 "왜 막히는지" 한 줄 설명(DB 커밋 후에만 오프셋 커밋, 그 사이에 죽으면 재전달되지만 inbox가 막음). 사용자는 "직접 고칠지, 튜터가 고칠지"를 아직 정하지 않았다. 그다음 ④ CQRS.
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
