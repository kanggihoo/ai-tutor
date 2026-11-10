# 레슨 06 외부 크레이트 쓰기 (2026-11-02 ~ 2026-11-10)

## 이론 요약
- 크레이트 = 외부 Rust 코드 묶음. `cargo add 이름`이 `Cargo.toml`의 `[dependencies]`에 등록 (Python `uv add`).
- `Cargo.toml` = 허용 버전 범위, `Cargo.lock` = 실제 고정 버전. `cargo update`는 Cargo.lock만, `cargo remove`는 둘 다 바꾼다.
- `cargo tree --depth 1` = 직접 의존성 확인. features = 기본 기능에 추가 기능을 켜는 스위치.
- `use serde_json::json;`은 짧은 이름 연결. 안 쓰면 `serde_json::json!(...)` 전체 경로로 써도 된다.
- 소스는 `~/.cargo/registry/src/.../크레이트-버전/`에 내려받아져 있다. `grep -rn "pub fn 이름"`으로 공개 함수를 찾고, 위 `///` 주석이 docs.rs 설명이다.
- docs.rs = 그 소스 주석을 보여 주는 사이트. 에러가 나거나 처음 보는 함수일 때 확인. 버전은 `Cargo.toml`과 맞춘다.

## 퀴즈와 정답
- `json!({ "port": port })`에서 변수를 값 자리에 쓰면 그 값이 들어간다 → `8080` (확인).
- `rand::random_range(1..=6)` 비교 출력 → `true` (확인, `06_rand_q1`).
- `rand::thread_rng()` → 컴파일 안 됨 E0425. 0.10.3에는 `rand::rng()`, `random_range`가 있다 (확인, `06_rand_q2`).

## 실전
- `06_rand_q2` 고치기는 사용자 요청으로 건너뜀 (파일은 깨진 채로 남김, 사용자 실행 안 함).

## 크레이트 추가
- `serde_json 1.0.154`, `rand 0.10.3` (`lab/`).

## 틀린 것·약점
- `cargo update`가 바꾸는 파일을 처음엔 "둘 다"로 답함.
- "소유권을 빌렸다" 표현이 재등장.
- 2026-11-10 복습 퀴즈 2개를 둘 다 "된다"고 예측 (E0596 `let mut` 누락, `&str`→`&String` E0308).
