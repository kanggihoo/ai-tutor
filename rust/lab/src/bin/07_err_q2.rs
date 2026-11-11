fn main() {
    let port: u16 = "abc".parse().unwrap_or(8080);
    println!("port: {}", port);
    let n: i32 = "x7".parse().expect("숫자 아님");
    println!("n: {}", n);
}
