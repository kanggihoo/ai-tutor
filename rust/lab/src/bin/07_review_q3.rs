fn double(text: &str) -> Result<i32, std::num::ParseIntError> {
    let n: i32 = text.parse()?;
    Ok(n * 2)
}

fn main() {
    println!("{:?}", double("21"));
    println!("{:?}", double("abc").is_err());
}
