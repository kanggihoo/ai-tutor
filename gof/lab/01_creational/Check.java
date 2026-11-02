// 실행: java Check.java   (이 파일은 고치지 않는다)
public class Check {
    static int failed = 0;

    static void check(String name, boolean ok, String detail) {
        System.out.println((ok ? "✅ " : "❌ ") + name + (ok ? "" : "  → " + detail));
        if (!ok) failed++;
    }

    public static void main(String[] args) {
        // Builder: 요구대로 주문이 만들어졌나
        OrderRequest o = Orders.sample();
        check("Builder: 금액 30000, 포인트 1000", o.amount() == 30000 && o.point() == 1000,
              "amount=" + o.amount() + ", point=" + o.point());

        // Prototype: 복제본을 고쳐도 원본은 그대로인가
        Cart original = Cart.of("kim", "커피", "케이크");
        Cart again = original.copy();
        again.items.add("쿠키");
        check("Prototype: 복제본 수정이 원본에 안 번짐", original.items.size() == 2,
              "원본 items=" + original.items);

        // Singleton: 테스트 두 개가 서로에게 영향을 주지 않나
        boolean eventOk = eventTest();
        boolean defaultOk = defaultTest();
        check("Singleton: 이벤트 수수료 10%", eventOk, "이벤트 테스트 실패");
        check("Singleton: 기본 수수료 3% (이벤트 테스트 뒤에 실행)", defaultOk,
              "앞 테스트가 바꾼 값이 남아 있음");

        System.out.println(failed == 0 ? "\n🎯 전부 통과" : "\n" + failed + "개 실패");
        System.exit(failed == 0 ? 0 : 1);
    }

    // 이 두 함수는 고쳐도 된다 (Singleton을 고치면 호출 방식이 바뀌므로)
    static boolean eventTest() {
        PaymentConfig.getInstance().feeRate = 10;
        return new FeeCalculator().fee(10000) == 1000;
    }

    static boolean defaultTest() {
        return new FeeCalculator().fee(10000) == 300;
    }
}
