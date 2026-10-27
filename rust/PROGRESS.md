# Rust 진행 현황 (튜터가 매 퀴즈/실전 후 갱신 · Mac/Windows 공통)

튜터 규칙은 [AGENTS.md](AGENTS.md), 질문 기록은 [QNA.md](QNA.md), 레슨별 복습 노트는 [notes/](notes/)에 있습니다.

## 프로필
- 목표: AI가 짠 Rust 코드를 읽고 판단하고 지휘하기. 손으로 많이 짜는 것은 목표가 아님.
- 학습 방식: 이론 짧게 → 예측 퀴즈 → 실전(고치기·리뷰·지휘). 모르는 건 질문하며 진행하고, 질문은 문서로 남김.
- 다른 언어 경험 (2026-10-27): Python·Java·C++는 알고리즘 풀이로 써 봄, TypeScript는 React 개발에서 써 봄. 이론 비교 기준: 소유권은 C++(복사/이동, 소멸자), `Option`/`Result`는 TS의 `T | undefined`와 Java 예외, 트레이트는 Java 인터페이스·TS 인터페이스, `enum`은 TS 유니언 타입.
- Rust로 해 보고 싶은 것 (2026-10-27): **Tauri 데스크톱 앱**(React/TS 프론트 + Rust 백엔드) 또는 **CLI 도구**. 예시 코드와 미니 프로젝트를 이쪽으로 맞춘다(`#[tauri::command]`, `serde`, `clap`).
- nvim 과목 기록상 선호: 세션당 20~30분, 문서 정독보다 대화로 한 문제씩, 쉬운 건 빠르게 넘어가길 원함. "이걸 쓸 일이 있나?"를 자주 물으므로 실제 쓰임새를 함께 알려 준다.

## 커리큘럼 (문법 + 실무 개발 흐름. 🛠 = 실무 레슨)
| # | 레슨 | 핵심 | 상태 |
|---|---|---|---|
| 01 | 🛠 Cargo 시작 | `cargo new/run/check/build --release`, `Cargo.toml`의 `[package]`, `Cargo.lock`, `target/`(uv·pyproject 비교), `let`/`mut`, 함수, `println!` | ✅ |
| 02 | 소유권 | move, `Copy`, `clone`, 스코프와 drop (`&`/`&mut`는 미리보기만) | 🔄 |
| 03 | 빌림 | `&`/`&mut`, 빌림 규칙, `String` vs `&str`, 슬라이스 | ⬜ |
| 04 | 구조체 | `struct`, `impl`, `self`/`&self`/`&mut self`, `Type::new()` 관례 | ⬜ |
| 05 | 열거형과 패턴 | `enum`, `match`, `if let`, `Option` | ⬜ |
| 06 | 🛠 외부 크레이트 쓰기 | `cargo add/remove/tree/update`, `[dependencies]`·버전 표기·features, `::` 경로와 `use`, docs.rs 읽는 법, `serde_json`·`rand` 실제로 써 보기 | ⬜ |
| 07 | 🛠 실무 에러 처리 | `Result`, `?`, `unwrap`/`expect`를 쓸 때와 피할 때, `anyhow`(앱)·`thiserror`(라이브러리), `.context()`, `main`에서 에러 반환, `RUST_BACKTRACE=1` | ⬜ |
| 08 | 모듈과 프로젝트 구조 | `mod`, `pub`, `use`, `crate::`/`super::`, 파일 분리, `main.rs`+`lib.rs`, 워크스페이스 | ⬜ |
| 09 | 🛠 속성과 derive 실전 | `#[derive(Debug, Clone, PartialEq)]`, `serde`로 JSON↔구조체(`#[serde(rename)]`), `clap`의 `#[derive(Parser)]`, `#[allow]`, `#[cfg]` | ⬜ |
| 10 | 트레이트와 제네릭 | `trait`, `impl Trait for`, `impl Trait`, `T: Trait`, `Display`/`From` | ⬜ |
| 11 | 컬렉션과 반복자 | `Vec`, `HashMap`, `iter`/`map`/`filter`/`collect`, 클로저 | ⬜ |
| 12 | 🛠 테스트와 품질 도구 | `#[test]`, `#[cfg(test)]`, `tests/` 폴더, `cargo test`, `cargo fmt`, `cargo clippy` 경고 읽고 고치기, `dbg!`, `cargo doc --open` | ⬜ |
| 13 | 라이프타임 읽기 | `'a`가 보이면 무슨 뜻인지, 언제 필요한지(작성보다 읽기) | ⬜ |
| 14 | 스마트 포인터와 공유 | `Box`, `Rc`, `Arc`, `Mutex` (읽기용) | ⬜ |
| 15 | 🛠 async와 HTTP | `async`/`await`, `#[tokio::main]`, `reqwest`로 API 호출, `.env` 설정값 읽기 | ⬜ |
| 16 | 🛠 미니 프로젝트 ① CLI | `clap` + `serde` + `anyhow`로 CLI 도구. `cargo install --path .`로 설치해서 실제로 쓰기. 요구사항은 사용자, 구현은 AI, 설명·리뷰는 사용자 | ⬜ |
| 17 | 🛠 미니 프로젝트 ② Tauri | React/TS + `#[tauri::command]`, 공유 상태, 프론트로 에러 전달, 빌드 | ⬜ |

상태: ⬜ 안 함 · 🔄 진행 중 · ✅ 완료

## 약점 (Weak spots)
- 불변 기본(`let` vs `let mut`)을 처음엔 놓침 (Q1, 2026-10-27)
- 섀도잉(같은 이름 `let` 재선언) 낯설어함, 블록 안 섀도잉 출력 순서 처음엔 헷갈림 (Q2)
- `;` 유무에 따른 반환값 (Q3: 처음엔 "문제 없다"고 답함)
- `cargo run --bin <이름>` 사용법 (파일 경로를 넣음)
- 복습 2에서 에러 여부를 묻는데 고치는 법만 답함. 질문에 먼저 답하는 습관 필요 (2026-10-28)
- `&`를 정의·호출 양쪽에 써야 하는 이유(`&String`과 `String`은 다른 타입)를 질문으로 확인함. 이후 C++과 비교도 질문함 (2026-10-28)

## 확인한 진도
"확인"은 cargo로 결과를 본 것, "설명만"은 안내만 하고 확인하지 못한 것.

| 레슨 | 항목 | 상태 |
|---|---|---|
| 01 | 퀴즈 Q1 불변 변수 재대입 에러 | 확인 (처음엔 오답, 이후 정정) |
| 01 | 퀴즈 Q2 섀도잉 출력 `hi`/`10` | 확인 (재질문 후 정답, 실행은 튜터가 함) |
| 01 | 퀴즈 Q3 `;` 때문에 반환 타입 불일치 | 확인 (실전 문제에서 같은 에러를 사용자가 직접 고침) |
| 01 | 실전 고치기 `01_fix_p1`, clippy, `--release` 실행 | 확인 (사용자가 직접 실행) |
| 02 | 복습 1 섀도잉 `40`/`4` | 확인 (정답, 튜터가 컴파일) |
| 02 | 복습 2 `;` 때문에 E0308 | 확인 (처음엔 고치는 법만 답하고, 되묻자 "컴파일 안 됨" 정답) |
| 02 | 퀴즈 Q1 move 후 사용 E0382 | 확인 (사용자가 직접 `cargo run`, 에러·`help:` 읽음) |
| 02 | 퀴즈 Q2 `i32` Copy `5 5` | 설명만 (예측 정답, 사용자 실행 미확인) |
| 02 | 퀴즈 Q3 `.clone()` 전달 `KIM!`/`kim 3` | 설명만 (예측 정답, 사용자 실행 미확인) |
| 02 | 실전 고치기 `02_fix_p1` | 진행 중: 튜터가 E0382로 안 컴파일되는 것 확인. 사용자는 두 방법(A `.clone()`, B `&` 정의·호출 둘 다)을 말로 답함, 아직 직접 고치지 않음 |

## 세션 로그
- 2026-10-26~27 (Mac): 과목 구조 생성, 저장소를 `ai-tutor`로 이름 변경(nvim/ · rust/ 분리), 프로필 확인. 학습 방식(이론 → 예측 퀴즈 → 실전)과 기록 방식(PROGRESS·QNA·notes) 확정. 레슨 진행은 아직 안 함.

- 2026-10-27 (Windows): 레슨 01 이론·퀴즈 완료. Windows 툴체인 확인(cargo/rustc 1.97.1, clippy 0.1.97, rust-analyzer 없음). 질문 6개 QNA 기록.

- 2026-10-28 (Mac): 복습 2문제, 레슨 02 이론(처음 설명), 퀴즈 Q1~Q3 완료. 실전 `02_fix_p1`은 문제만 낸 상태. 질문 3개(`&`/`&mut`, `&` 양쪽 필요, C++ 참조 비교)는 QNA.md에 아직 미기록.

## 다음 단계
1. **레슨 02 이론은 2026-10-28에 처음 설명함**(이전 기록의 "이론 끝"은 실제와 달랐음). move, Copy, clone, drop, `&`/`&mut` 미리보기, 시그니처 읽는 법까지 전달함.
2. 이어서 할 것: `lab/src/bin/02_fix_p1.rs` 실전 고치기. `cd rust/lab && cargo run --bin 02_fix_p1`로 에러를 읽고 한 줄 요약 → 방법 A(`msg.clone()`)와 B(`text: &String` + `count_chars(&msg)`)로 각각 통과시키고 → 어느 쪽이 나은지 이유 말하기. 기대 출력 `안녕 rust 는 7글자`. 일부러 한쪽에만 `&`를 붙여 E0308도 보게 한다.
3. 그다음: 실전 리뷰(불필요한 `clone` 찾기 문제 새로 만들기), `notes/02-ownership.md` 작성, QNA.md에 이번 질문 기록(`&` 양쪽에 필요한 이유, C++ 참조와 비교, `&mut`).
4. Q2·Q3는 사용자가 `cargo run --bin`으로 직접 확인하게 한다.
5. 다음 세션 복습 퀴즈: 섀도잉, `;` 반환(복습 2를 다시), move vs Copy.
