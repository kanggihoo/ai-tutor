struct Todo { title: String, done: bool }

impl Todo {
    fn new(title: String) -> Todo {
        Todo { title: title, done: false }
    }
    fn title(&self) -> String {
        self.title
    }
    fn finish(&mut self) {
        self.done = true;
    }
    fn is_done(&self) -> bool {
        self.done
    }
}

fn main() {
    let mut todo = Todo::new(String::from("rust"));
    todo.finish();
    println!("{}", todo.is_done());
    println!("{}", todo.title());
}
