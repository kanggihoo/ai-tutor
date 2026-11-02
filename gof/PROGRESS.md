# GoF 디자인 패턴 진행 현황 (튜터가 체크포인트·질문마다 갱신)

튜터 규칙은 [AGENTS.md](AGENTS.md), 23개 지도와 제외 이유는 [README.md](README.md)에 있습니다.

## 프로필
- 요청 (2026-11-03): GoF 23개 중 요즘 잘 쓰는 것 위주로 빠르게 코드로 확인. 생성 패턴은 빠르게 넘어가도 됨.
- 결정 (2026-11-03): Java 25(빌드 도구 없이 `java Check.java`), 도메인은 주문·결제, 실습 11 / 판독 7 / 제외 5.
- 다른 언어 경험: Python·Java·C++(알고리즘), TypeScript(React). SSAFY 교육생.
- 선호: 세션당 20~30분, 대화로 한 문제씩, 쉬운 건 빠르게. "이걸 쓸 일이 있나?"를 자주 물음. 과설계를 싫어함.

## 체크포인트
| # | 묶음 | 상태 | 메모 |
|---|---|---|---|
| 01 | 생성 빠른 점검 | ⬜ | 코드 준비됨: `lab/01_creational/`. 지금은 ❌ 3개(Builder, Prototype, Singleton 기본 수수료). 정답 수정은 튜터가 임시 폴더에서 통과 확인 (2026-11-03) |
| 02 | 감싸기 (Adapter·Decorator·Proxy + Facade) | ⬜ | |
| 03 | 교체 (Strategy·State + Template Method·Composite) | ⬜ | |
| 04 | 요청 처리 (Observer·CoR·Command + Memento) | ⬜ | |
| 05 | 예비, 지도 정리 | ⬜ | |

상태: ⬜ 안 함 · 🔄 진행 중 · ✅ 완료

## 01 튜터 메모 (정답, 사용자에게 먼저 보여 주지 않는다)
- Builder: `Orders.sample()`을 `OrderRequest.builder("kim").amount(30000).point(1000).gift(true).build()`로. 질문: "인자 순서만 고쳐도 통과하는데 왜 Builder를 쓰나?"
- Prototype: `copy()`에서 `new ArrayList<>(items)`. 질문: "`customer`(String)는 왜 같이 복사하지 않아도 되나?" (불변)
- Singleton: `FeeCalculator(int feeRate)` 생성자로 받고, `Check`의 두 테스트 함수를 `new FeeCalculator(10)`, `new FeeCalculator(3)`으로. 질문: "Spring 빈은 싱글톤인데 왜 이런 문제가 덜 생기나?"
- 판독: Factory Method vs 정적 팩토리, Abstract Factory, Iterator는 코드 조각을 그 자리에서 보여 주고 이유 한 줄.

## 약점
(아직 없음)

## 다음 단계
01 생성 빠른 점검. 시작 질문: "`java Check.java`를 실행하면 몇 개가 실패할까요? 코드부터 훑어보고 맞혀 보세요."
