const chatInput = document.getElementById('dango-chat-input');
const chatMessages = document.getElementById('dango-chat-messages');
const chatForm = document.getElementById('dango-chat-form');
function dangoSendMsg(e){
    e.preventDefault();
    const msg = chatInput.value.trim();
    if(!msg) return;
    chatMessages.innerHTML += `<div class="dango-message user">Ви: ${msg}</div>`;
    chatInput.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;
    fetch("/shop/chat-api/", {
        method: "POST",
        headers: {"X-CSRFToken": window.CSRF_TOKEN, "Content-Type": "application/x-www-form-urlencoded"},
        body: `message=${encodeURIComponent(msg)}`
    }).then(r=>r.json()).then(data=>{
        chatMessages.innerHTML += `<div class="dango-message bot">Бот: ${data.answer}</div>`;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }).catch(()=>{
        chatMessages.innerHTML += `<div class="dango-message bot text-danger">Помилка зв'язку</div>`;
    });
}