struct Account { owner: String, balance: u32 }

impl Account {
    fn new(owner: &str) -> Account {
        Account { owner: owner.to_string(), balance: 0 }
    }
    fn deposit(&mut self, amount: u32) {
        self.balance += amount;
    }
    fn owner(&self) -> &str {
        &self.owner
    }
}

fn main() {
    let mut acc = Account::new("kim");
    acc.deposit(500);
    println!("{} {}", acc.owner(), acc.balance);
}
