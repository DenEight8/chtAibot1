// static/shop/js/chat.js
document.addEventListener('DOMContentLoaded', () => {
    const chatbox      = document.getElementById('chatbox');
    const fab          = document.getElementById('chat-fab');
    const closeBtn     = document.getElementById('chat-close-btn');
    const chatForm     = document.getElementById('chat-form');
    const chatInput    = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    if (!chatbox || !fab || !closeBtn || !chatForm || !chatInput || !chatMessages) return;

    /* ── show / hide ───────────────────────────────────────── */
    fab.addEventListener('click', () => {
        chatbox.style.opacity = '1';
        chatbox.style.pointerEvents = 'auto';
        fab.style.display = 'none';
    });
    closeBtn.addEventListener('click', () => {
        chatbox.style.opacity = '0';
        chatbox.style.pointerEvents = 'none';
        fab.style.display = '';
    });

    /* ── local history ────────────────────────────────────── */
    let history = [];
    try {
        const stored = localStorage.getItem('dango_chat_history');
        history = stored ? JSON.parse(stored) : [];
    } catch (e) {
        history = [];
        alert('Помилка при завантаженні історії чату. Історія буде скинута.');
        localStorage.removeItem('dango_chat_history');
    }

    const esc = s => s.replace(/[&<>"'`=\/]/g,
        c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;','`':'&#96;','=':'&#61;','/':'&#47;'}[c]));

    const saveHistory = () => {
        try {
            localStorage.setItem('dango_chat_history', JSON.stringify(history));
        } catch (e) {
            // Можна показати користувачу повідомлення, або записати у консоль
            // alert('Помилка збереження історії чату.');
            console.warn('Помилка збереження історії чату.');
        }
    };

    const render = () => {
        chatMessages.innerHTML = history
            .map(m => `<div style="margin-bottom:4px;"><b style="color:${m.role==='bot'?'#cb3a00':'#222'}">${m.role==='bot'?'Bot':'Ви'}:</b> ${esc(m.text)}</div>`)
            .join('');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    render();

    /* ── send ─────────────────────────────────────────────── */
    chatForm.addEventListener('submit', ev => {
        ev.preventDefault();
        const msg = chatInput.value.trim();
        if (!msg) return;

        history.push({ role: 'user', text: msg });
        render();
        saveHistory();

        const csrf = chatForm.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        fetch('/api/chat/', {
            method : 'POST',
            headers: {
                'X-CSRFToken' : csrf,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept'      : 'application/json'
            },
            body   : new URLSearchParams({ message: msg })
        })
        .then(r => {
            if (!r.ok) throw new Error('Server error');
            return r.json();
        })
        .then(j => {
            let cls =
                j.type === "error" ? "⚠️" :
                j.type === "gpt"   ? "🤖" :
                j.type === "faq"   ? "📚" : "";
            let text = (typeof j.answer === 'string' && j.answer.trim()) ? `${cls} ${j.answer}`.trim() : '[empty]';
            history.push({ role: "bot", text });
            render();
            saveHistory();
        })
        .catch(err => {
            history.push({ role: 'bot', text: '[Помилка чату]' });
            render();
            saveHistory();
        });

        chatInput.value = '';
    });

    /* ── clear history (RMB) ──────────────────────────────── */
    chatMessages.addEventListener('contextmenu', e => {
        e.preventDefault();
        if (confirm('Очистити історію чату?')) {
            history = [];
            localStorage.removeItem('dango_chat_history');
            render();
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('chatbot-container');
    const header = container?.querySelector('.chatbot-header');
    if (!container || !header) return;

    container.style.position = 'fixed';
    const pos = JSON.parse(localStorage.getItem('chatbotPos') || 'null');
    const size = JSON.parse(localStorage.getItem('chatbotSize') || 'null');
    if (size) {
        container.style.width = size.width + 'px';
        container.style.height = size.height + 'px';
    }
    if (pos) {
        container.style.left = pos.left + 'px';
        container.style.top = pos.top + 'px';
    } else {
        container.style.right = '1rem';
        container.style.bottom = '1rem';
    }

    const handle = document.createElement('div');
    handle.className = 'chatbot-resize-handle';
    container.appendChild(handle);

    let drag = false, offsetX = 0, offsetY = 0;
    header.addEventListener('mousedown', e => {
        drag = true;
        offsetX = e.clientX - container.offsetLeft;
        offsetY = e.clientY - container.offsetTop;
        document.body.style.userSelect = 'none';
    });

    let resize = false, startX = 0, startY = 0, startW = 0, startH = 0;
    handle.addEventListener('mousedown', e => {
        resize = true;
        startX = e.clientX;
        startY = e.clientY;
        startW = container.offsetWidth;
        startH = container.offsetHeight;
        document.body.style.userSelect = 'none';
        e.stopPropagation();
    });

    const clamp = (val, min, max) => Math.min(Math.max(val, min), max);
    const savePos = () => localStorage.setItem('chatbotPos', JSON.stringify({
        left: container.offsetLeft,
        top: container.offsetTop
    }));
    const saveSize = () => localStorage.setItem('chatbotSize', JSON.stringify({
        width: container.offsetWidth,
        height: container.offsetHeight
    }));

    document.addEventListener('mousemove', e => {
        if (drag) {
            const vw = document.documentElement.clientWidth;
            const vh = document.documentElement.clientHeight;
            let l = e.clientX - offsetX;
            let t = e.clientY - offsetY;
            l = clamp(l, 0, vw - container.offsetWidth);
            t = clamp(t, 0, vh - container.offsetHeight);
            container.style.left = l + 'px';
            container.style.top = t + 'px';
        } else if (resize) {
            let w = startW + e.clientX - startX;
            let h = startH + e.clientY - startY;
            w = clamp(w, 320, 560);
            h = clamp(h, 260, 720);
            container.style.width = w + 'px';
            container.style.height = h + 'px';
        }
    });

    document.addEventListener('mouseup', () => {
        if (drag) {
            drag = false;
            document.body.style.userSelect = '';
            savePos();
        }
        if (resize) {
            resize = false;
            document.body.style.userSelect = '';
            saveSize();
        }
    });
});