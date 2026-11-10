use rand::random_range;

fn main() {
    let n = random_range(1..=6);
    println!("{}", n >= 1 && n <= 6);
}
