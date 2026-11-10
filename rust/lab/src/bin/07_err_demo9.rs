fn f(o: Option<String>) -> Option<usize> {
    let s = o?;
    println!("{}", o.is_some());
    Some(s.len())
}

fn main() {
    println!("{:?}", f(Some("hi".to_string())));
}
