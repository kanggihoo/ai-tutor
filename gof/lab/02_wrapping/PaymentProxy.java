// 실제 결제 앞에 서서 권한을 확인하는 대리 객체
class PaymentProxy implements Payment {
    private final Payment target;
    private final User user;

    PaymentProxy(Payment target, User user) {
        this.target = target;
        this.user = user;
    }

    // 결정 지점: 권한 확인을 언제 하나?
    public String pay(int amount) {
        String result = target.pay(amount);
        if (!user.canPay()) throw new IllegalStateException("결제 권한 없음: " + user.name());
        return result;
    }
}
