fn main() {
    let output = Some(String::from("report.pdf"));

    if let Some(filename) = &output {
        println!("save to: {filename}");
    }

    match &output {
        Some(name) => println!("setting: {name}"),
        None => println!("no output setting"),
    }
}
