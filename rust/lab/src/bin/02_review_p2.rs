fn shout(name: &String) -> String {
    format!("{}!", name.to_uppercase())
}

fn name_len(name: &String) -> usize {
    name.chars().count()
}

fn main() {
    let user = String::from("kim");
    let loud = shout(&user);
    let len = name_len(&user);
    let copy = user.clone();
    println!("{loud} {len} {copy}");
}
