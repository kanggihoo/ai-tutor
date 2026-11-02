# 04 구조체

## 핵심
- 필드는 `struct`, 메서드는 `impl`에 쓴다. Java의 클래스와 달리 상속은 없다.
- `&self`는 읽기 빌림, `&mut self`는 수정 빌림, `self`는 소유권 이동이다.
- 수정 메서드 호출에는 호출 변수도 `let mut`이어야 한다. `self` 없는 연관 함수는 `Type::new()`로 부른다.

```rust
struct Todo { title: String }
impl Todo {
    fn title(&self) -> &str { &self.title }
}
```

`String`은 문자열을 소유하고 `&str`은 빌려 읽는다. 위의 `&String`은 반환 타입에 맞춰 `&str`로 자동 변환된다. `bool` 같은 Copy 값은 `&self`에서도 복사해서 반환할 수 있다.

## 퀴즈와 정답
- Q1: `let u`에서 `&mut self` 메서드 호출 → E0596. `let mut u` 필요.
- Q2: `&self` 메서드에서 필드 수정 → E0594. 수정하려면 `&mut self` 필요.
- Q3: `into_name(self)` 뒤 `u.age` 사용 → E0382. `u` 전체가 이동한다.
- 처음에는 세 문제 모두 오답. 2026-11-02 복습에서는 수정 빌림 호출과 소비 후 사용 불가를 맞힘. cargo check 확인.

## 실전
- `lab/src/bin/04_fix_p1.rs`: 메서드의 `&mut self`와 호출 변수의 `let mut` 수정. 사용자 직접 실행 `kim 500`.
- `lab/src/bin/04_review_p1.rs`: 읽기 메서드 `is_done`을 `&self`로 변경. 제목 getter는 아래 원래 형태에서 소비와 호출부 clone을 피하도록 개선.

```rust
fn title(self) -> String { self.title }
```

중간 수정 `fn title(&self) -> String { self.title }`은 E0507. 최종 수정은 위 예시의 `&str` 반환이다. 사용자 직접 실행 `true`/`rust`, 튜터 파일 확인. 반복 호출 가능한 이유를 사용자가 "소유권이 이동하지 않았기 때문"이라고 설명함.

## 헷갈린 점과 남은 항목
- `String`/`&str`, 값 빌림과 소유권 이동, `&String` → `&str` 자동 변환을 재설명함.
- 리뷰 문제의 심각도 분류와 잘한 점 답변은 미확인. `title: title`은 `title`로 줄일 수 있으나 파일에는 원형 유지.
- 지휘 문제는 사용자 요청으로 건너뜀(2026-11-02).
