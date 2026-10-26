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
| 01 | 🛠 Cargo 시작 | `cargo new/run/check/build --release`, `Cargo.toml`의 `[package]`, `Cargo.lock`, `target/`(uv·pyproject 비교), `let`/`mut`, 함수, `println!` | ⬜ |
| 02 | 소유권 | move, `Copy`, `clone`, 스코프와 drop | ⬜ |
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
- (아직 없음)

## 확인한 진도
"확인"은 cargo로 결과를 본 것, "설명만"은 안내만 하고 확인하지 못한 것.

| 레슨 | 항목 | 상태 |
|---|---|---|

## 세션 로그
- 2026-10-26~27 (Mac): 과목 구조 생성, 저장소를 `ai-tutor`로 이름 변경(nvim/ · rust/ 분리), 프로필 확인. 학습 방식(이론 → 예측 퀴즈 → 실전)과 기록 방식(PROGRESS·QNA·notes) 확정. 레슨 진행은 아직 안 함.

## 다음 단계
1. 레슨 01 시작: `lab/`의 `Cargo.toml`부터 같이 읽는다.
