fn shout(s: String) -> usize {
    println!("{}!", s.to_uppercase());
    s.len()
}

fn main() {
    let name = String::from("kim");
    let n = shout(name.clone());
    println!("{name} {n}");
}
