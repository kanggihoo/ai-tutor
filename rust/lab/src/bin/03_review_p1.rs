fn greet(name: &str) {
    println!("안녕하세요, {name}!");
}

fn main() {
    let name = String::from("kim");
    greet(&name);
    greet("lee");
    println!("로그인: {name}");
}
