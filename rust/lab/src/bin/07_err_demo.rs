fn parse_port(s: &str) -> Result<u16, std::num::ParseIntError> {
    let n = s.parse::<u16>()?;
    Ok(n)
}

fn main() {
    println!("{:?}", parse_port("80"));
    println!("{:?}", parse_port("abc"));
}
