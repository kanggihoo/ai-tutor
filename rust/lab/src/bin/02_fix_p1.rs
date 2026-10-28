fn count_chars(text: &String) -> usize {
    text.chars().count()
}

fn main() {
    let msg = String::from("안녕 rust");
    let n = count_chars(&msg);
    println!("{msg} 는 {n}글자");
}
