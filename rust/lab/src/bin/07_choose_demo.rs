fn find_name(id: u32) -> Option<String> {
    if id == 1 { Some(String::from("kim")) } else { None }
}

fn parse_port(text: &str) -> Result<u16, std::num::ParseIntError> {
    text.parse()
}

fn main() {
    println!("{:?}", find_name(2));
    println!("{:?}", parse_port("abc"));
    let first = [10, 20, 30][0];
    println!("{}", first);
}
