fn main() {
    let port: Option<u16> = Some(0);
    if let Some(number) = port {
        println!("port: {number}");
    }
    println!("done");
}
