fn g(o: &Option<String>) -> Option<usize> {
    let s = o.as_ref()?;
    Some(s.len())
}

fn main() {
    let o = Some("hi".to_string());
    println!("{:?}", g(&o));
    println!("{:?}", o);
}
