fn main() {
    let good = "80".parse::<u16>();
    let bad = "abc".parse::<u16>();

    if let Ok(n) = &good { println!("if let: {}", n); }
    println!("unwrap_or: {} {}", good.clone().unwrap_or(0), bad.clone().unwrap_or(0));
    println!("is_ok: {} {}", good.is_ok(), bad.is_ok());
    println!("map: {:?} {:?}", good.clone().map(|n| n + 1), bad.clone().map(|n| n + 1));
    println!("ok: {:?} {:?}", good.clone().ok(), bad.clone().ok());
    println!("map_err: {:?}", bad.clone().map_err(|e| format!("포트 변환 실패: {}", e)));
    println!("expect: {}", good.clone().expect("80은 숫자"));
}
