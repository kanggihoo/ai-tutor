fn add_bang(text: &mut String) {
    text.push('!');
}

fn main() {
    let mut s = String::from("hi");
    let a = &mut s;
    add_bang(a);
    let b = &mut s;
    add_bang(b);
    println!("{s}");
}
