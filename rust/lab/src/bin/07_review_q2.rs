fn len_of(s: &String) -> usize {
    s.len()
}

fn main() {
    let a = String::from("hello");
    println!("{}", len_of(&a[..]));
}
