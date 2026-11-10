fn a() -> Result<u16, String> {
    Err("망함".to_string())
}

fn b() -> Result<u16, String> {
    let n = a()?;
    println!("b: 여기까지 왔다");
    Ok(n)
}

fn main() {
    println!("main: b를 부른다");
    let r = b();
    println!("main: 받은 값 = {:?}", r);
}
