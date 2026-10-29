struct User { name: String, age: u32 }

impl User {
    fn birthday(&mut self) { self.age += 1; }
}

fn main() {
    let mut u = User { name: String::from("kim"), age: 20 };
    u.birthday();
    println!("{} {}", u.name, u.age);
}
