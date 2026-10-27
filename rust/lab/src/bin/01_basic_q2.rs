fn main() {
    let x = 5;
    let x = x * 2;
    {
        let x = "hi";
        println!("{x}");
    }
    println!("{x}");
}
