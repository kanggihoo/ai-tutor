# Rust 진행 현황 (튜터가 매 퀴즈/실전 후 갱신 · Mac/Windows 공통)

튜터 규칙은 [AGENTS.md](AGENTS.md), 질문 기록은 [QNA.md](QNA.md), 레슨별 복습 노트는 [notes/](notes/)에 있습니다.

## 프로필
- 목표: AI가 짠 Rust 코드를 읽고 판단하고 지휘하기. 손으로 많이 짜는 것은 목표가 아님.
- 학습 방식: 이론 짧게 → 예측 퀴즈 → 실전(고치기·리뷰·지휘). 모르는 건 질문하며 진행하고, 질문은 문서로 남김.
- 다른 언어 경험 (2026-10-27): Python·Java·C++는 알고리즘 풀이로 써 봄, TypeScript는 React 개발에서 써 봄. 이론 비교 기준: 소유권은 C++(복사/이동, 소멸자), `Option`/`Result`는 TS의 `T | undefined`와 Java 예외, 트레이트는 Java 인터페이스·TS 인터페이스, `enum`은 TS 유니언 타입.
- Rust로 해 보고 싶은 것 (2026-10-27): **Tauri 데스크톱 앱**(React/TS 프론트 + Rust 백엔드) 또는 **CLI 도구**. 예시 코드와 미니 프로젝트를 이쪽으로 맞춘다(`#[tauri::command]`, `serde`, `clap`).
- nvim 과목 기록상 선호: 세션당 20~30분, 문서 정독보다 대화로 한 문제씩, 쉬운 건 빠르게 넘어가길 원함. "이걸 쓸 일이 있나?"를 자주 물으므로 실제 쓰임새를 함께 알려 준다.

## 커리큘럼 (실제 코드에서 자주 보이는 순서)
| # | 레슨 | 핵심 | 상태 |
|---|---|---|---|
| 01 | Cargo와 프로젝트 구조 읽기 | `Cargo.toml`, `main.rs`/`lib.rs`, `cargo run/check/test/clippy`, `let`/`mut`, 함수, `println!` | ⬜ |
| 02 | 소유권 | move, `Copy`, `clone`, 스코프와 drop | ⬜ |
| 03 | 빌림 | `&`/`&mut`, 빌림 규칙, `String` vs `&str`, 슬라이스 | ⬜ |
| 04 | 구조체 | `struct`, `impl`, `self`/`&self`/`&mut self`, `new` 관례 | ⬜ |
| 05 | 열거형과 패턴 | `enum`, `match`, `if let`, `Option` | ⬜ |
| 06 | 에러 처리 | `Result`, `?`, `unwrap`/`expect`를 쓸 때와 피할 때, `anyhow`/`thiserror` 맛보기 | ⬜ |
| 07 | 모듈 | `mod`, `pub`, `use`, `crate::`/`super::`, 파일 분리, 외부 크레이트 | ⬜ |
| 08 | 속성 `#[...]` | `#[derive(Debug, Clone, PartialEq)]`, `#[cfg(test)]`/`#[test]`, `#[allow]`, `#[serde(...)]`, `#[tokio::main]` 미리보기 | ⬜ |
| 09 | 트레이트와 제네릭 | `trait`, `impl Trait for`, `impl Trait`, `T: Trait`, `Display`/`From` | ⬜ |
| 10 | 컬렉션과 반복자 | `Vec`, `HashMap`, `iter`/`map`/`filter`/`collect`, 클로저 | ⬜ |
| 11 | 라이프타임 읽기 | `'a`가 보이면 무슨 뜻인지, 언제 필요한지(작성보다 읽기) | ⬜ |
| 12 | 스마트 포인터와 공유 | `Box`, `Rc`, `Arc`, `Mutex` (읽기용) | ⬜ |
| 13 | async 읽기 | `async`/`await`, `tokio`, `Future` 감 잡기 | ⬜ |
| 14 | 미니 프로젝트 지휘 | ① `clap` CLI 도구 → ② Tauri 앱(`#[tauri::command]`로 React에서 Rust 호출). 요구사항은 사용자, 구현은 AI, 설명·리뷰는 사용자 | ⬜ |

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
