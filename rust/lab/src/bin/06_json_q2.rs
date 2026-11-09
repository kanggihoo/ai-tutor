

fn main() {
    let config = serde_json::json!({ "port": 8080, "enabled": true });
    println!("{}", config["port"]);
    println!("{}", config["enabled"]);
}
