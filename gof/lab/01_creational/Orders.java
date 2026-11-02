class Orders {
    // 요구: kim, 결제 금액 30000원, 포인트 1000점 사용, 선물 포장
    static OrderRequest sample() {
        return new OrderRequest("kim", 1000, 30000, true); // 결정 지점
    }
}
