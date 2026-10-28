fn greet(name: &String) {
    println!("안녕하세요, {name}!");
}

fn main() {
    let name = String::from("kim");
    greet(&name.clone());
    println!("로그인: {name}");
}
