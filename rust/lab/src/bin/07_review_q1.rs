struct Counter {
    n: u32,
}

impl Counter {
    fn add(&mut self) {
        self.n += 1;
    }
}

fn main() {
    let c = Counter { n: 0 };
    c.add();
    println!("{}", c.n);
}
