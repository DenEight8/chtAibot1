// static/shop/js/chat.js
document.addEventListener('DOMContentLoaded', () => {
    const chatbox      = document.getElementById('chatbox');
    const fab          = document.getElementById('chat-fab');
    const closeBtn     = document.getElementById('chat-close-btn');
    const chatForm     = document.getElementById('chat-form');
    const chatInput    = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    if (!chatbox || !fab || !closeBtn || !chatForm || !chatInput || !chatMessages) return;
    const header       = chatbox.querySelector('.chat-header');
    const resizer      = chatbox.querySelector('.chat-resizer');

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

    /* ── dragging ─────────────────────────────────────────── */
    if (header) {
        header.addEventListener('pointerdown', e => {
            if (e.button !== 0) return;
            e.preventDefault();
            const rect = chatbox.getBoundingClientRect();
            const shiftX = e.clientX - rect.left;
            const shiftY = e.clientY - rect.top;
            const onMove = ev => {
                chatbox.style.left = ev.clientX - shiftX + 'px';
                chatbox.style.top = ev.clientY - shiftY + 'px';
                chatbox.style.right = 'auto';
                chatbox.style.bottom = 'auto';
            };
            const onUp = () => {
                document.removeEventListener('pointermove', onMove);
            };
            document.addEventListener('pointermove', onMove);
            document.addEventListener('pointerup', onUp, { once: true });
        });
    }

    /* ── resizing ─────────────────────────────────────────── */
    if (resizer) {
        resizer.addEventListener('pointerdown', e => {
            e.preventDefault();
            const startW = chatbox.offsetWidth;
            const startH = chatbox.offsetHeight;
            const startX = e.clientX;
            const startY = e.clientY;
            const onMove = ev => {
                const newW = Math.max(240, startW + ev.clientX - startX);
                const newH = Math.max(180, startH + ev.clientY - startY);
                chatbox.style.width = newW + 'px';
                chatbox.style.height = newH + 'px';
            };
            const onUp = () => {
                document.removeEventListener('pointermove', onMove);
            };
            document.addEventListener('pointermove', onMove);
            document.addEventListener('pointerup', onUp, { once: true });
        });
    }

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