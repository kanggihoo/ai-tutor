fn main() {
    let port: Option<u16> = Some(8080);
    match port {
        Some(number) => println!("port: {number}"),
        None => println!("default port"),
    }
}
