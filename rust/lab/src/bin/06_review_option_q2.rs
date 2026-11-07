fn main() {
    let output = Some(String::from("report.pdf"));
    if let Some(filename) = &output {
        println!("save: {filename}");
    }
    match output {
        Some(name) => println!("setting: {name}"),
        None => println!("unset"),
    }
}
