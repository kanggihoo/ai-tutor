fn main() {
    let use_expect = true; // false로 바꿔서 다시 실행
    if use_expect {
        let a: i32 = "abc".parse().expect("PORT는 숫자여야 함");
        println!("{}", a);
    } else {
        let a: i32 = "abc".parse().unwrap();
        println!("{}", a);
    }
}
