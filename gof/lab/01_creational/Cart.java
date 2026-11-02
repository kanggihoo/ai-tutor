import java.util.ArrayList;
import java.util.List;

// Prototype: 기존 장바구니를 복제해서 "다시 주문하기"를 만든다.
class Cart {
    final String customer;
    final List<String> items;

    Cart(String customer, List<String> items) {
        this.customer = customer;
        this.items = items;
    }

    Cart copy() {
        return new Cart(customer, items); // 결정 지점: 복제본과 원본이 무엇을 공유하나?
    }

    static Cart of(String customer, String... items) {
        return new Cart(customer, new ArrayList<>(List.of(items)));
    }
}
