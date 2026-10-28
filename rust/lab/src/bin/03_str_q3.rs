fn main() {
    let mut s = String::from("hello world");
    s.push('!');
    let w = &s[0..5];
    println!("{w} {s}");
}
