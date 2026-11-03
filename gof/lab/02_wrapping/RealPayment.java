// 실제 PG 호출 자리 (가짜). 몇 번 불렸는지만 센다.
class RealPayment implements Payment {
    int calls = 0;

    public String pay(int amount) {
        calls++;
        return "paid:" + amount;
    }
}
