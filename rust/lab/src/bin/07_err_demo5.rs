use std::fs;

struct Guard;
impl Drop for Guard {
    fn drop(&mut self) { println!("정리(finally처럼 자동 실행)"); }
}

fn read_port(path: &str) -> Result<u16, String> {
    let _g = Guard;
    let text = fs::read_to_string(path)
        .map_err(|e| format!("파일 읽기 실패 {}: {}", path, e))?;
    let n = text.trim().parse::<u16>()
        .map_err(|e| format!("숫자 변환 실패: {}", e))?;
    Ok(n)
}

fn main() {
    match read_port("없는파일.txt") {
        Ok(n) => println!("포트 {}", n),
        Err(e) => println!("main이 받음: {}", e),
    }
}
