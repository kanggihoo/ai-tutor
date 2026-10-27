fn celsius_to_fahrenheit(c: f64) -> f64 {
    c * 9.0 / 5.0 + 32.0
}

fn main() {
    let temp = 20.0;
    let  temp = celsius_to_fahrenheit(temp);
    let mut count = 0;
    println!("{temp}도");
    count = count + 1;
}
