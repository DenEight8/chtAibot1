document.addEventListener('DOMContentLoaded', () => {
    const chatbox      = document.getElementById('chatbox');
    const fab          = document.getElementById('chat-fab');
    const closeBtn     = document.getElementById('chat-close-btn');
    const chatForm     = document.getElementById('chat-form');
    const chatInput    = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    if (!chatbox || !fab || !closeBtn || !chatForm || !chatInput || !chatMessages) return;

    // show / hide
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

    // local history
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

    // send
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

    // clear history (RMB)
    chatMessages.addEventListener('contextmenu', e => {
        e.preventDefault();
        if (confirm('Очистити історію чату?')) {
            history = [];
            localStorage.removeItem('dango_chat_history');
            render();
        }
    });

    // DRAG & RESIZE функціонал
    const container =
        document.getElementById('chatbot-container') ||
        document.getElementById('chatbox');
    if (!container) return;

    const header = container.querySelector('.chatbot-header') ||
        container.firstElementChild;
    if (!header) return;

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

    let drag = false, offsetX = 0, offsetY = 0;

    const savePos = () => localStorage.setItem('chatbotPos', JSON.stringify({
        left: container.offsetLeft,
        top: container.offsetTop
    }));
    const saveSize = () => localStorage.setItem('chatbotSize', JSON.stringify({
        width: container.offsetWidth,
        height: container.offsetHeight
    }));

    header.addEventListener('mousedown', e => {
        drag = true;
        offsetX = e.clientX - container.offsetLeft;
        offsetY = e.clientY - container.offsetTop;
        document.body.style.userSelect = 'none';
    });
    header.addEventListener('touchstart', e => {
        const t = e.touches[0];
        if (!t) return;
        drag = true;
        offsetX = t.clientX - container.offsetLeft;
        offsetY = t.clientY - container.offsetTop;
        document.body.style.userSelect = 'none';
    }, { passive: true });

    const move = (x, y) => {
        if (!drag) return;
        container.style.left = (x - offsetX) + 'px';
        container.style.top = (y - offsetY) + 'px';
    };

    document.addEventListener('mousemove', e => move(e.clientX, e.clientY));
    document.addEventListener('touchmove', e => {
        const t = e.touches[0];
        if (t) move(t.clientX, t.clientY);
    }, { passive: false });

    const endDrag = () => {
        if (!drag) return;
        drag = false;
        document.body.style.userSelect = '';
        savePos();
    };
    document.addEventListener('mouseup', endDrag);
    document.addEventListener('touchend', endDrag);

    new ResizeObserver(saveSize).observe(container);
});
