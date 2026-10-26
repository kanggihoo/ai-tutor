# Rust 질문 기록

실습 중 물어본 것을 튜터가 답한 직후 주제별로 적습니다. `복습` 표시가 붙은 항목은 세션 시작 복습 퀴즈에 나옵니다. 형식은 [AGENTS.md](AGENTS.md)의 "기록"을 보세요.

## 소유권·빌림

## 타입·구조체·열거형

## 에러 처리

## 모듈·Cargo·크레이트

### Q. Cargo.toml은 uv의 pyproject.toml과 비슷한가?
- 2026-10-27 · 레슨 01 전 · 복습
- 답: 거의 같은 역할이다. `[package]`≈`[project]`, `[dependencies]`≈`dependencies`, `[dev-dependencies]`≈dev 그룹, `features`≈extras, `Cargo.lock`≈`uv.lock`, crates.io≈PyPI. 명령도 `cargo add/remove/run/tree`≈`uv add/remove/run/tree`, `cargo install`≈`uv tool install`, `cargo fmt`/`clippy`≈`ruff format`/`ruff check`. 차이: Rust는 컴파일 언어라 `.venv` 대신 `target/`에 빌드 결과가 쌓이고, 가상환경 없이 의존성이 프로젝트와 함께 컴파일된다. 툴체인 버전은 rustup(`rust-toolchain.toml`)이 맡는다(uv의 `.python-version`과 비슷).
- 한 줄 요약: Cargo = uv + ruff + 빌드 도구를 합친 것.

### Q. `::`는 뭔가? 외부 패키지를 쓸 때 많이 보이던데
- 2026-10-27 · 레슨 06 예고 · 복습
- 답: 경로 구분자다. 모듈·타입의 경로는 `::`, 값의 메서드는 `.`으로 나눠 쓴다. `std::fs::read_to_string("a.txt")`는 표준 라이브러리 `fs` 모듈의 함수, `serde_json::from_str(s)`는 외부 크레이트의 함수, `String::new()`는 타입에 붙은 함수(Python의 클래스 메서드와 비슷)다. 매번 길게 쓰기 싫으면 `use serde_json::Value;`처럼 가져온다(Python의 `from ... import`).
- 한 줄 요약: `::`는 "어디에 있는 무엇"(경로), `.`은 "이 값의 메서드".

## 속성 `#[...]`

## 트레이트·제네릭

## 컬렉션·반복자

## 기타
