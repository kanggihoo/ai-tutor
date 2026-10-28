fn main() {
    let mut s = String::from("hi");
    let a = &s;
    let b = &s;
    println!("{a} {b}");
    let c = &mut s;
    c.push('!');
    println!("{c}");
}
