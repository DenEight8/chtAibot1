// site.js

document.addEventListener("DOMContentLoaded", function() {
    // AJAX-додавання у кошик
    let form = document.getElementById("add-to-cart-form");
    if (form) {
        form.addEventListener("submit", function(e) {
            e.preventDefault();
            let url = form.action;
            let formData = new FormData(form);
            fetch(url, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.cart_count !== undefined) {
                    // Оновлюємо бейдж кошика скрізь, де він є
                    document.querySelectorAll(".cart-count-badge").forEach(el => {
                        el.textContent = data.cart_count;
                    });
                }
            })
            .catch(err => {
                alert("Помилка додавання у кошик");
            });
        });
    }
});
