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
| 01 | 생성 빠른 점검 | 🔄 | 코드 준비됨: `lab/01_creational/`. 지금은 ❌ 3개(Builder, Prototype, Singleton 기본 수수료). 정답 수정은 튜터가 임시 폴더에서 통과 확인 (2026-11-03) |
| 02 | 감싸기 (Adapter·Decorator·Proxy + Facade) | 🔄 | Adapter·Decorator 대화 학습. Proxy 개념 설명 후 `lab/02_wrapping/` 실습 중 (❌ 1개: 권한 없을 때 실제 결제 호출됨). 정답(권한 확인을 target 호출 앞으로)은 임시 폴더에서 통과 확인 (2026-11-03) |
| 03 | 교체 (Strategy·State + Template Method·Composite) | ⬜ | |
| 04 | 요청 처리 (Observer·CoR·Command + Memento) | ⬜ | |
| 05 | 예비, 지도 정리 | ⬜ | |

상태: ⬜ 안 함 · 🔄 진행 중 · ✅ 완료

## 01 튜터 메모 (정답, 사용자에게 먼저 보여 주지 않는다)
- Builder: `Orders.sample()`을 `OrderRequest.builder("kim").amount(30000).point(1000).gift(true).build()`로. 질문: "인자 순서만 고쳐도 통과하는데 왜 Builder를 쓰나?"
- Prototype: `copy()`에서 `new ArrayList<>(items)`. 질문: "`customer`(String)는 왜 같이 복사하지 않아도 되나?" (불변)
- Singleton: `FeeCalculator(int feeRate)` 생성자로 받고, `Check`의 두 테스트 함수를 `new FeeCalculator(10)`, `new FeeCalculator(3)`으로. 질문: "Spring 빈은 싱글톤인데 왜 이런 문제가 덜 생기나?"
- 판독: Factory Method vs 정적 팩토리, Abstract Factory, Iterator는 코드 조각을 그 자리에서 보여 주고 이유 한 줄.

## 2026-11-03 학습 기록
- Builder: 인자 의미 명시와 유지보수 이점을 설명함. 좌표처럼 인자가 적어도 혼동이 잦으면 도입 근거가 있다는 의견. Lombok @Builder로 반복 구현 비용을 줄일 수 있음을 짚음.
- Prototype: 처음에는 새 Cart면 리스트도 독립적이라고 예상. 이후 참조 공유를 이해하고 새 리스트에 기존 원소를 넣는 수정을 스스로 제안함. 불변 String은 공유 가능하고 문자열 덧붙이기는 기존 문자열을 수정하지 않음을 이해함.
- Prototype 활용: 기존 주문·문서·설정 복제. 비싼 초기화 결과를 재사용할 수 있지만 복사가 항상 빠른 것은 아니며, 변경할 데이터는 독립적으로 복사해야 함을 설명.
- Singleton·Iterator: 이미 익숙하다는 사용자 요청으로 생략(검증 없음).
- Factory Method: 부모 공통 흐름에서 자식이 생성 방법을 정함. Spring DI로 충분한 결제 예제에는 필요성이 약하다는 사용자 지적. 상속 기반 라이브러리의 생성 확장 지점으로 설명(판독 검증 없음).
- Abstract Factory: 관련 객체의 생성을 묶고 팩토리를 교체하면 제품군이 함께 바뀌는 구조로 설명. 사용자는 관련 객체를 만드는 클래스로 이해(판독 검증 없음).
- Adapter: 외부 SDK를 우리 Payment 인터페이스에 연결하고 SDK 호출 변경을 어댑터에 모으는 구조를 사용자 스스로 설명함. Payment p = new VendorPaymentAdapter(...)로 사용함을 이해.
- Decorator: 같은 Payment를 구현하는 객체로 기존 Payment를 감싸 로깅 등 기능 추가. 같은 인터페이스 구현은 원래 객체 자리에 대입하고 여러 겹 조합하기 위한 것임을 설명.
- Python 연결: 함수를 받고 감싼 함수를 반환하는 고차 함수와 함수 데코레이터 비교. Python @ 문법 전체가 GoF Decorator를 뜻하지는 않음.
- Spring 연결: 공통 로깅은 AOP로 적용 가능. Spring AOP는 프록시 기반이며 Decorator와 동의어는 아님. 어노테이션은 정보, 리플렉션은 런타임 조사·호출 수단. @Override처럼 컴파일 시 처리하는 예외도 설명.
- Proxy: 권한 검사로 실제 결제 호출을 제한하는 코드를 제시했으나 응답 전 종료. 사용자 요청으로 다음 시간에 처음부터 다시 진행.

- (2026-11-03 2차) 복습: Adapter=외부 SDK 변경 흡수 중간다리, Decorator=기존 코드 유지하고 앞뒤 기능 추가로 정확히 답함. 보충: Adapter는 인터페이스 모양 변환도, Decorator는 여러 겹 쌓기 가능.
- Proxy는 완전 처음이라는 사용자 지적 → 실습 전에 개념부터(비서 비유, Decorator와 의도 비교, @Transactional·JPA 지연 로딩). **새 패턴은 개념 먼저, 실습은 그 다음.**
- 네트워크 프록시와 같은 아이디어(앞에서 받아 처리 후 진짜로 전달)라고 스스로 연결함. 질문: Spring 어노테이션 중 AOP와 리플렉션 처리 구분 → 기준 "호출 앞뒤에 끼어드나", 자기 호출(this.method())이 깨지면 프록시. @Valid(컨트롤러, 프록시 아님) vs @Validated(서비스, 프록시) 설명(설명만).
- 튜터 실수: 깨진 체크포인트 코드를 "일부러 틀린 것"이라고 밝히지 않고 보여 줘서 혼란과 불만. **깨진 코드는 처음부터 "버그 있는 버전"이라고 말한다.**
- Proxy 실습은 사용자 요청("다음")으로 생략. 정답만 알려 줌. `lab/02_wrapping/`은 ❌ 1개 그대로, 지도 체크 안 함.
- Facade: 개념(여러 호출 → 메서드 하나, Adapter와 대비) 설명 후 판독 질문 "repository.save() 하나만 위임하는 OrderService도 Facade인가?" (정답 방향: 단순화할 여러 호출이 없으니 Facade라 부를 근거 약함)

## 실행 확인과 남은 점
- 이번 세션은 대화 학습. 실습 코드는 수정하지 않았으며 실행 통과도 확인하지 않음. README 지도는 통과 체크하지 않음.
- 기존 준비 기록: lab/01_creational은 실패 3개 상태이며 정답은 이전 준비 시 임시 폴더에서 검증했다고 기록되어 있음. 이번 세션에서 재확인한 결과는 아님.
- 이번 java Check.java는 다른 소스 클래스를 찾지 못해 컴파일 실패. 기본 java -version은 Microsoft OpenJDK 21.0.11로 확인. 규정된 Java 25 실행 경로 확인이 필요함.
- 대화에서는 실용성과 Spring DI·AOP와의 관계를 먼저 설명하면 이해가 빠름. 익숙한 내용은 사용자 요청대로 빠르게 생략.

## 다음 단계
1. **Facade를 이론부터 다시 시작한다.** 지난 판독 질문(OrderService)은 답하지 않았으니 답했다고 가정하지 않는다.
2. 시작 멘트: "지난번엔 Proxy를 개념으로 봤고, 오늘은 Facade를 처음부터 볼게요."
3. 짧은 복습 1개: Proxy와 Decorator는 구조가 같은데 무엇이 다른가 (기대 답: 기능 추가 vs 접근 관리, 진짜를 부를지·언제 부를지 Proxy가 결정).
4. Facade 개념: 여러 객체를 정해진 순서로 부르는 과정을 메서드 하나로 묶는 창구. 예제는 PG 인증·승인·영수증 3개 호출을 묶은 `checkout()`. Adapter와 대비(대상 하나·인터페이스 변환 vs 여러 개·호출 단순화). 실무 예: 회원가입 시 저장·쿠폰·메일을 묶은 `signUp()`.
5. 판독: `repository.save()` 하나만 위임하는 OrderService도 Facade인가? (정답 방향: 단순화할 여러 호출이 없으니 근거 약함. 서비스 계층이라서 Facade인 것은 아님)
6. 이후 감싸기 과용 리뷰 1개 → 03 교체 묶음.
7. `lab/02_wrapping/` Proxy 실습은 ❌ 1개 상태로 남아 있음. 05 예비에서 재도전 가능.
8. 새 패턴은 개념을 먼저 설명하고, 깨진 코드는 "버그 있는 버전"이라고 먼저 밝힌다.
