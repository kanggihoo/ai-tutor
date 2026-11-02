# 05 열거형과 패턴

## 핵심
- enum은 가능한 종류 중 하나를 담고 종류별 데이터를 붙인다. TypeScript 유니언과 비슷하다.
- match는 패턴에 따라 갈래를 선택하고 내부 값을 새 변수에 받는다. 모든 경우를 처리해야 한다.
- Option<T>는 Some(T) 또는 None이다. Java Optional과 목적이 비슷하다. if let은 특정 패턴에 맞을 때만 실행한다.

```rust
let output = Some(String::from("report.pdf"));
if let Some(filename) = &output {
    println!("save to: {filename}");
}
```

Some(filename)은 패턴이며 filename은 새 이름이다. &output을 검사하므로 filename은 &String이다. 문자열 복사나 이동 없이 원본을 읽는다.

## 퀴즈와 정답
- `05_enum_q1`: Done(42)를 Done(size)로 받으면 `42 MB`. u32가 복사된다. 사용자 판단 정답, 출력 문구 보완. 튜터 실행 확인.
- `05_enum_q2`: 원래 Waiting 갈래 누락으로 E0004. 사용자 에러 요약 후 갈래 추가·직접 실행 성공. never constructed는 해당 값을 만든 적 없다는 경고다.
- `05_enum_q3`: 원래 내부 String이 name으로 이동한 뒤 state 전체를 saved로 옮겨 E0382(부분 이동). 힌트 후 사용자 오류 위치 정답. match &state로 수정·직접 실행 성공.
- Option/if let 추가 예제는 튜터 실행 확인. 사용자 출력 예측 답변은 미확인.

## 실전 리뷰
경로: `lab/src/bin/05_review_p1.rs`

원래 문제:
```rust
if output.is_some() {
    let filename = output.clone().unwrap();
    println!("save to: {filename}");
}
```

사용자가 `if let Some(filename) = &output`을 제안하고 수정했다. clone/unwrap 없이 읽고 뒤의 match에서도 output을 쓴다. 사용자 실행 보고 후 튜터 파일·cargo run 확인. 출력은 `save to: report.pdf`와 `setting: report.pdf`.

원래 코드도 이 흐름에서는 Some 확인 후 unwrap하므로 None으로 중단되지는 않는다. 불필요한 복사·중복 처리를 줄이는 권장 개선이다. 사용자에게 분류 질문은 생략했고 잘한 점 답변은 미확인이다.

## 헷갈린 점
- if let의 =는 패턴 매칭 문법이다. Copy 전용 문법이 아니다.
- u32는 복사, String은 이동, 검사 대상을 &로 빌리면 내부 값도 빌린다.
- unwrap은 None에서 실행을 중단(패닉)한다. unwrap_or는 기본값으로 계속 진행한다.
- Some(0), Some("")는 값이 있는 상태다.
- bool 인자→enum, 표시값→Option, let else는 미실습.

다음: 레슨 06 외부 크레이트 쓰기.
