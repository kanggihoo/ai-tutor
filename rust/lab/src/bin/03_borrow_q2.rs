fn main() {
    let mut s = String::from("hi");
    let a = &s;
    println!("{a}");
    let c = &mut s;
    c.push('!');
    println!("{c}");
}
