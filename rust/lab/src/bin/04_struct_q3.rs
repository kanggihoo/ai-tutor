struct User { name: String, age: u32 }

impl User {
    fn new(name: &str, age: u32) -> User {
        User { name: name.to_string(), age }
    }
    fn into_name(self) -> String { self.name }
}

fn main() {
    let u = User::new("kim", 20);
    let n = u.into_name();
    println!("{} {}", n, u.age);
}
