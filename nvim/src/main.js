import { config } from "./config.js";
import { calculateTotal, validateCoupon } from "./services/orders.js";

const order = { subtotal: 15000, region: "seoul" };
const total = calculateTotal(order.subtotal, order.region);

console.log("DEBUG: checkout preview", order);
console.log(config.storeName, total);
console.log(validateCoupon({ expired: true }));

ORDER
