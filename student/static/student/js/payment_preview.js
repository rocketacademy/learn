$(function () {
  const payable_type = document.getElementById("payable-type").value;
  const payable_id = document.getElementById("payable-id").value;
  const payable_line_item_name = document.getElementById(
    "payable-line-item-name"
  ).value;
  const payable_line_item_amount_in_cents = document.getElementById(
    "payable-line-item-amount-in-cents"
  ).value;
  const payable_line_item_amount_in_cents_hk = document.getElementById(
    "payable-line-item-amount-in-cents-hk"
  ).value;
  const payment_success_path = document.getElementById(
    "payment-success-path"
  ).value;
  const payment_cancel_path = document.getElementById(
    "payment-cancel-path"
  ).value;
  let stripe_coupon_id = document.getElementById("stripe-coupon-id").value;
  if (stripe_coupon_id == "None") {
    stripe_coupon_id = null;
  }
  let stripe_coupon_id_hk = document.getElementById(
    "stripe-coupon-id-hk"
  ).value;
  if (stripe_coupon_id_hk == "None") {
    stripe_coupon_id_hk = null;
  }

  fetch("/payment/stripe/config/")
    .then((result) => {
      return result.json();
    })
    .then((data) => {
      const stripe = Stripe(data.publicKey);

      // SG payment button
      document
        .querySelector("#make-payment-button")
        .addEventListener("click", () => {
          fetch("/payment/stripe/create-checkout-session/", {
            method: "POST",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              currency: "sgd",
              payable_type: payable_type,
              payable_id: payable_id,
              payable_line_item_name: payable_line_item_name,
              payable_line_item_amount_in_cents:
                payable_line_item_amount_in_cents,
              payment_success_path: payment_success_path,
              payment_cancel_path: payment_cancel_path,
              stripe_coupon_id: stripe_coupon_id,
            }),
          })
            .then((result) => {
              return result.json();
            })
            .then((data) => {
              return stripe.redirectToCheckout({ sessionId: data.sessionId });
            });
        });

      // HK payment button
      document
        .querySelector("#make-payment-button-hk")
        .addEventListener("click", () => {
          fetch("/payment/stripe/create-checkout-session/", {
            method: "POST",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              currency: "hkd",
              payable_type: payable_type,
              payable_id: payable_id,
              payable_line_item_name: payable_line_item_name,
              payable_line_item_amount_in_cents:
                payable_line_item_amount_in_cents_hk,
              payment_success_path: payment_success_path,
              payment_cancel_path: payment_cancel_path,
              stripe_coupon_id: stripe_coupon_id_hk,
            }),
          })
            .then((result) => {
              return result.json();
            })
            .then((data) => {
              return stripe.redirectToCheckout({ sessionId: data.sessionId });
            });
        });
    });
});
