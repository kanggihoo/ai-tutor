# 레슨 01 · 🛠 Cargo 시작 (2026-10-27, Windows)

## 이론 요약
1. 변수는 기본 불변. 바꾸려면 `let mut`. `let`을 다시 쓰면 재대입이 아니라 **새 변수(섀도잉)**이고 타입도 바꿀 수 있다. 블록 안 섀도잉은 블록이 끝나면 사라진다.
2. 함수 마지막 줄에 `;`가 없으면 그 값이 반환값. `;`가 붙으면 `()`가 되어 타입 불일치 에러. `return`은 중간 탈출용.
3. Cargo: `run`(빌드+실행), `check`(실행 파일 없이 검사), `build`(빌드만), `--release`(최적화), `clippy`(린터), `fmt`(포매터).

```rust
fn double(n: i32) -> i32 {
    n * 2          // ; 없음 → 반환값
}
```

| Cargo | uv |
|---|---|
| `Cargo.toml` / `Cargo.lock` | `pyproject.toml` / `uv.lock` |
| `target/` (빌드 산출물) | `.venv/`와 달리 환경이 아니라 결과물 |
| `cargo run` | `uv run` |

## 퀴즈와 정답 (`lab/src/bin/01_basic_q1~q3.rs`)
- Q1 `let x = 5; x = x + 1;` → 컴파일 에러(불변 변수 재대입, 3번째 줄). 고치려면 `let mut x`.
- Q2 `let x = 5; let x = x * 2; { let x = "hi"; println!("{x}"); } println!("{x}");` → `hi`, `10`.
- Q3 `fn add_one(n: i32) -> i32 { n + 1; }` → 에러(`;` 때문에 `()` 반환). `;` 제거 또는 `return n + 1;`.

## 실전: 고치기 (`lab/src/bin/01_fix_p1.rs`)
- 원래 문제: `celsius_to_fahrenheit` 마지막 줄 `c * 9.0 / 5.0 + 32.0;`의 `;` 때문에 컴파일 실패. 파일은 `;`를 지운 풀린 상태로 남아 있다.
- 남은 경고: `count = count + 1;` 은 대입한 값을 아무도 읽지 않음(rustc `unused_assignments`). clippy는 추가로 `count += 1`을 제안(`assign_op_pattern`). 판단: 지우거나, 실제로 쓰거나.
- 출력: `68도`.
- 확인한 것: `cargo check`, `cargo run --bin`, `cargo clippy`, `cargo run --release`(`target\release\...exe` 실행).

## 정리한 것
- `cargo run --bin <이름>`은 파일 경로가 아니라 바이너리 이름. 실제 프로젝트는 `src/main.rs` 하나라 `cargo run`만 쓴다.
- `target/debug`는 빠른 컴파일·느린 실행, `target/release`는 느린 컴파일·빠른 실행. `.exe`만 실행 파일, `.pdb`(디버그 심볼)·`.d`(의존 목록)는 부산물. 크레이트 소스는 전역 캐시, 버전과 빌드는 프로젝트별.
- 경고는 "변수가 안 쓰임"이 아니라 "**대입한 값이** 안 읽힘"일 수 있다.

## 틀린 것
- Q1 불변 변수 재대입을 처음엔 놓침, Q3 `;`를 "문제 없다"고 답함.
- `cargo run --release`를 "빌드만 한다"고 답함(실제로는 빌드+실행).
- `cargo run`에 파일 경로를 넣음.
