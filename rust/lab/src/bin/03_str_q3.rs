fn main() {
    let mut s = String::from("hello world");
    let w = &s[0..5];
    s.push('!');
    println!("{w} {s}");
}
