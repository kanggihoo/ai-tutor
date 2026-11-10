fn h(o: &Option<String>) -> Option<usize> {
    let s = o?;
    Some(s.len())
}

fn main() {
    let o = Some("hi".to_string());
    println!("{:?}", h(&o));
}
