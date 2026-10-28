fn main() {
    let x = 4;
    { let x = x * 10; println!("{x}"); }
    println!("{x}");
}
