fn len_of(s: &str) -> usize {
    s.len()
}

fn main() {
    let owned = String::from("hi");
    let lit = "hello";
    println!("{} {}", len_of(&owned), len_of(lit));
}
