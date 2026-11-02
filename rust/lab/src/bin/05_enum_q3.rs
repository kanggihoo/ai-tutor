enum Download {
    Waiting,
    Done(String),
}

fn main() {
    let state = Download::Done(String::from("report.pdf"));
    match &state {
        Download::Waiting => println!("waiting"),
        Download::Done(name) => println!("{name}"),
    }
    let saved = state;
}
