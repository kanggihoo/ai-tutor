fn first_char(s: &str) -> Option<char> {
    let c = s.chars().next()?;
    Some(c)
}

fn main() {
    println!("{:?} {:?}", first_char("hi"), first_char(""));
}
