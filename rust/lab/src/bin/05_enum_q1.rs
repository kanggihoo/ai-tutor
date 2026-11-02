enum Download {
    Waiting,
    Done(u32),
}

fn main() {
    let state = Download::Done(42);
    match state {
        Download::Waiting => println!("waiting"),
        Download::Done(size) => println!("{size} MB"),
    }
}
