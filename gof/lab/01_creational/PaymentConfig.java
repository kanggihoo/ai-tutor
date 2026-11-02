// Singleton: 결제 수수료율을 앱 전체에서 하나로 공유한다.
class PaymentConfig {
    private static final PaymentConfig INSTANCE = new PaymentConfig();

    static PaymentConfig getInstance() {
        return INSTANCE;
    }

    int feeRate = 3; // %
}
