enum Download {
    Waiting,
    Done(u32),
}

fn main() {
    let state = Download::Done(42);
    match state {
        Download::Done(size) => println!("{size} MB"),
        Download::Waiting => println!("waiting"),
    }
}
