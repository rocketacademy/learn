$(function () {
  const payable_type = document.getElementById("payable-type").value;
  const payable_id = document.getElementById("payable-id").value;
  fetch("/payment/config/")
    .then((result) => {
      return result.json();
    })
    .then((data) => {
      const stripe = Stripe(data.publicKey);
      document
        .querySelector("#make-payment-button")
        .addEventListener("click", () => {
          fetch(
            "/payment/create-checkout-session/" +
              payable_type +
              "/" +
              payable_id +
              "/"
          )
            .then((result) => {
              return result.json();
            })
            .then((data) => {
              return stripe.redirectToCheckout({ sessionId: data.sessionId });
            });
        });
    });
});
