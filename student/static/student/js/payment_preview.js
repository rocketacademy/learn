$(function () {
  const payable_type = document.getElementById("payable-type").value;
  const payable_id = document.getElementById("payable-id").value;
  const payable_line_item_name = document.getElementById(
    "payable-line-item-name"
  ).value;
  const payable_line_item_amount_in_cents = document.getElementById(
    "payable-line-item-amount-in-cents"
  ).value;
  const payment_success_path = document.getElementById(
    "payment-success-path"
  ).value;
  const payment_cancel_path = document.getElementById(
    "payment-cancel-path"
  ).value;
  const stripe_coupon_id = document.getElementById(
    "stripe-coupon-id"
  ).value;

  fetch("/payment/stripe/config/")
    .then((result) => {
      return result.json();
    })
    .then((data) => {
      const stripe = Stripe(data.publicKey);
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
              payable_type: payable_type,
              payable_id: payable_id,
              payable_line_item_name: payable_line_item_name,
              payable_line_item_amount_in_cents:
                payable_line_item_amount_in_cents,
              payment_success_path: payment_success_path,
              payment_cancel_path: payment_cancel_path,
              stripe_coupon_id: stripe_coupon_id
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
