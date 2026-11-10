fn check_age(age: i32) -> Result<i32, String> {
    if age < 0 {
        return Err(format!("나이가 음수: {}", age));
    }
    Ok(age)
}

fn main() {
    match check_age(-1) {
        Ok(a) => println!("ok {}", a),
        Err(e) => println!("실패: {}", e),
    }
    panic!("강제 종료");
}
