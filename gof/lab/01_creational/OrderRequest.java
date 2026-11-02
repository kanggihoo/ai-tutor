// Builder: 같은 타입(int) 인자가 나란히 있는 생성자.
record OrderRequest(String customer, int amount, int point, boolean gift) {

    static Builder builder(String customer) {
        return new Builder(customer);
    }

    static class Builder {
        private final String customer;
        private int amount;
        private int point;
        private boolean gift;

        Builder(String customer) { this.customer = customer; }
        Builder amount(int v) { amount = v; return this; }
        Builder point(int v) { point = v; return this; }
        Builder gift(boolean v) { gift = v; return this; }
        OrderRequest build() { return new OrderRequest(customer, amount, point, gift); }
    }
}
