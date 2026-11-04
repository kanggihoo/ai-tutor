# 외부 소재 지도 (튜터 준비용)

레슨을 준비할 때 해당 행만 본다. 선택 소재이며 숙제·진도가 아니다. 아래는 파일 확인만 마친 후보이고, 쓰기 전 lab(edition 2024)에서 컴파일한다.

## 출처
| 약칭 | 저장소 | 고정 커밋 | 라이선스 | 쓰는 법 |
|---|---|---|---|---|
| RBP | [sunface/rust-by-practice](https://github.com/sunface/rust-by-practice) (`en/src/`) | `fc561055b71b8356a78542e82794fa06d5fe00b0` | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | 문항을 예측·고치기·리뷰로 변형. 노트에 원문 링크·문항·변경 내용 기록 |
| RC | [sunface/rust-course](https://github.com/sunface/rust-course) (`src/`, 중국어) | `a4a7eead178464dfa2430a9c45e6478523ae549b` | No License (읽기만) | 튜터 읽기·주제 참고만. 원문·번역·코드를 옮기지 않고 문제는 새로 쓴다 |

- 원문 링크 형식: `https://github.com/sunface/rust-by-practice/blob/<커밋>/en/src/<경로>`
- RBP 예시는 edition 2021이다. 검증 결과는 `lab(2024), cargo run --bin …: 결과`로 적는다.
- RBP의 관례(예: 읽기 매개변수 `&String`)를 리뷰 기준으로 삼지 않는다. 기준은 AGENTS.md의 규칙 절.

## 레슨별 후보
| 레슨 | 후보 | 처리 |
|---|---|---|
| 01·02 | 없음 | — |
| 03 | RBP `ownership/borrowing.md`, `compound-types/string.md`·`slice.md` | 예측·고치기. `&String` 관례는 `&str`로 바꾸거나 리뷰 냄새로 역이용 |
| 04 | RBP `method.md` #2 | 수신자(`&self`/`self`) 복습이 필요할 때 |
| 05 | RBP `pattern-match/match-iflet.md`·`patterns.md` | 배운 범위의 예측형 |
| 06 | RC `cargo/guide/cargo-toml-lock.md`·`cargo/reference/features/intro.md`; RBP `crate-module/use-pub.md` #1 (선택) | RC 읽기. RBP는 `as` 별칭이 헷갈릴 때 고치기 |
| 07 | RBP `result-panic/result.md` #1~3·끝의 `main -> Result` 예제; RC `advance/errors.md` anyhow 절 | 장황한 `unwrap`/`match` → `?` 리뷰. `.context()`는 자체 제작 |
| 08 | RBP `crate-module/crate.md`·`module.md`; RC `cargo/guide/package-layout.md` | 구조 읽기·작은 고치기 |
| 09 | 없음 | serde·clap 자체 제작 |
| 10 | RBP `generics-traits/traits.md`·`generics.md`, `type-conversions/from-into.md` #2 | 읽기 위주, 과도한 일반화 문항 제외 |
| 11 | RBP `collections/`, `functional-programing/iterator.md`·`closure.md`; RC `compiler/pitfalls/lazy-iterators.md`(우선)·`use-vec-in-for.md`(선택) | RBP 변형. RC 주제는 요구사항상 버그가 명확한 예제로만 새로 작성 |
| 11 이후 | RBP `fight-compiler/borrowing.md` #1; RC `compiler/pitfalls/the-disabled-mutability.md`·`multiple-mutable-references.md` | 04·11 통합 복습 (`self` 재빌림) |
| 12 | RC `compiler/pitfalls/arithmetic-overflow.md` (선택) | 프로필 설정(`overflow-checks`)을 명시한 자체 문제 |
| 13 | RBP `lifetime/basic.md` #2·#3 | 참조 유효성 예측, 완성 코드 읽기 |
| 14 | RBP `smart-pointers/box.md` #3 | 이동 복습 겸 도입. `Rc`/`Arc`/`Mutex`는 자체 제작 |
| 15~17 | 없음 | 16 이후 사용자가 원하면 RBP `elegant-code-base.md` 링크만 |

## 쓰지 않는 것
- RBP 빈 페이지: `tests/`, `async/`, `errors.md`, `smart-pointers/`(box 외).
- RBP `type-conversions/from-into.md` #3: 수동 `From`으로 자체 에러 타입. 앱 기준(anyhow) 흐름에서 우선순위 낮음.
- RC `compiler/pitfalls/` 중 `closure-with-lifetime`, `main-with-channel-blocked`, `stack-overflow`, `utf8-performance`: 목표(앱 코드 읽기)에서 빈도 낮음.
- RC `difficulties/` 전체 정독.
