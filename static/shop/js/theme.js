/* simple “add to cart” demo */
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".btn-add").forEach(btn => {
    btn.addEventListener("click", e => {
      e.preventDefault();
      const id = btn.dataset.id;
      fetch("/api/quick-order/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": getCookie("csrftoken")
        },
        body: `product_id=${id}&quantity=1`
      })
      .then(r => r.json())
      .then(_ => {
        const badge = document.getElementById("cart-count");
        badge.textContent = parseInt(badge.textContent || 0) + 1;
        btn.classList.add("added");
        btn.textContent = "✓ Додано";
        setTimeout(() => {
          btn.textContent = "У кошик";
          btn.classList.remove("added");
        }, 1500);
      });
    });
  });
});
function getCookie(n){let v=null;if(document.cookie){document.cookie.split(";")
.forEach(c=>{c=c.trim();if(c.startsWith(n+"="))v=decodeURIComponent(c.substring(n.length+1))})}return v;}
