#[derive(Debug)]
struct User { name: String, age: u32 }

#[derive(Debug)]
enum LoginError { NoUser, WrongPassword }

fn find_user(name: &str) -> Result<User, LoginError> {
    if name == "kim" {
        Ok(User { name: name.to_string(), age: 20 })
    } else {
        Err(LoginError::NoUser)
    }
}

fn main() {
    println!("{:?}", find_user("kim"));
    println!("{:?}", find_user("lee"));
    let _ = LoginError::WrongPassword;
}
