import { config } from "../config.js";

/** 주문 금액과 지역으로 배송비를 포함한 최종 금액을 계산합니다. */
export function calculateTotal(subtotal, region) {
  const delivery = subtotal >= config.freeShippingThreshold ? 0 : config.shippingFee;
  const surcharge = region === "jeju" ? config.jejuSurcharge : 0;
  return subtotal + delivery + surcharge;
}

export function validateCoupon(coupon) {
  if (coupon.expired) return "COUPON_EXPIRED";
  return "COUPON_OK";
}
