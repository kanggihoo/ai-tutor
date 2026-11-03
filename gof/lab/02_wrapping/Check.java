// 실행: java Check.java   (이 파일은 고치지 않는다)
public class Check {
    static int failed = 0;

    static void check(String name, boolean ok, String detail) {
        System.out.println((ok ? "✅ " : "❌ ") + name + (ok ? "" : "  → " + detail));
        if (!ok) failed++;
    }

    public static void main(String[] args) {
        // Proxy: 권한 있는 사용자는 그대로 결제된다
        RealPayment real = new RealPayment();
        Payment p = new PaymentProxy(real, new User("kim", true));
        check("Proxy: 권한 있으면 결제", "paid:1000".equals(p.pay(1000)) && real.calls == 1,
              "calls=" + real.calls);

        // Proxy: 권한 없는 사용자는 실제 결제까지 가면 안 된다
        RealPayment real2 = new RealPayment();
        Payment blocked = new PaymentProxy(real2, new User("guest", false));
        boolean thrown = false;
        try { blocked.pay(1000); } catch (IllegalStateException e) { thrown = true; }
        check("Proxy: 권한 없으면 예외", thrown, "예외가 안 남");
        check("Proxy: 권한 없으면 실제 결제 호출 0번", real2.calls == 0, "calls=" + real2.calls);

        System.out.println(failed == 0 ? "\n🎯 전부 통과" : "\n" + failed + "개 실패");
        System.exit(failed == 0 ? 0 : 1);
    }
}
