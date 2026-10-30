struct Counter { count: u32 }

impl Counter {
    fn new() -> Counter { Counter { count: 0 } }
    fn inc(&mut self) { self.count += 1; }
}

fn main() {
    let mut c = Counter::new();
    c.inc();
    println!("{}", c.count);
}
