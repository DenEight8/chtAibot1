$(function () {
    /* Маска телефону */
    $("#id_phone").mask("+38 (999) 999-99-99");

    /* Автопошук */
    if (typeof initSearch === "function") initSearch();

    /* WS-чат */
    const ws = new WebSocket(
        (location.protocol === "https:" ? "wss://" : "ws://") +
        location.host + "/ws/chat/"
    );
    ws.onmessage = ev => {
        const data = JSON.parse(ev.data);
        addBotMessage(data.answer);               // реалізуйте у chat.js
    };
    $("#chat-send-btn").on("click", () => {
        ws.send(JSON.stringify({message: $("#chat-input").val()}));
    });

    /* Швидке замовлення */
    if (typeof initQuickOrder === "function") initQuickOrder();
});
