class FeeCalculator {
    // 결정 지점: 수수료율을 어디서 받아 오나?
    int fee(int amount) {
        return amount * PaymentConfig.getInstance().feeRate / 100;
    }
}
