use serde_json::json;

fn main() {
    let config = json!({ "port": 8080, "enabled": true });
    println!("{}", config["port"]);
    println!("{}", config["enabled"]);
}
