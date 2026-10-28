fn main() {
    let mut values = [1, 2, 3];
    let part = &mut values[0..2];
    part[0] = 9;
    println!("{values:?}");
}
