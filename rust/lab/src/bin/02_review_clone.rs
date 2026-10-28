fn show_name(name: &String) {
    println!("사용자: {name}");
}

fn main() {
    let name = String::from("kim");
    show_name(&name.clone());
    println!("원본: {name}");
}
