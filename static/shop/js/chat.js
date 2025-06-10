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

    // додати handle для resize
    const handle = document.createElement('div');
    handle.className = 'chatbot-resize-handle';
    container.appendChild(handle);

    let drag = false, offsetX = 0, offsetY = 0;
    const startDrag = (x, y) => {
        drag = true;
        offsetX = x - container.offsetLeft;
        offsetY = y - container.offsetTop;
        document.body.style.userSelect = 'none';
    };

    header.addEventListener('mousedown', e => startDrag(e.clientX, e.clientY));
    header.addEventListener('touchstart', e => {
        const t = e.touches[0];
        if (t) startDrag(t.clientX, t.clientY);
    }, { passive: true });

    let resize = null;
    let startX = 0, startY = 0, startW = 0, startH = 0, startL = 0, startT = 0;
    const startResize = (x, y, edges) => {
        resize = edges;
        startX = x;
        startY = y;
        startW = container.offsetWidth;
        startH = container.offsetHeight;
        startL = container.offsetLeft;
        startT = container.offsetTop;
        document.body.style.userSelect = 'none';
    };
    handle.addEventListener('mousedown', e => {
        startResize(e.clientX, e.clientY, { right: true, bottom: true });
        e.stopPropagation();
    });
    handle.addEventListener('touchstart', e => {
        const t = e.touches[0];
        if (t) startResize(t.clientX, t.clientY, { right: true, bottom: true });
        e.stopPropagation();
    }, { passive: true });

    const EDGE_SIZE = 8;
    const getEdges = (x, y) => {
        const rect = container.getBoundingClientRect();
        const left   = x - rect.left <= EDGE_SIZE;
        const right  = rect.right - x <= EDGE_SIZE;
        const top    = y - rect.top <= EDGE_SIZE;
        const bottom = rect.bottom - y <= EDGE_SIZE;
        if (left || right || top || bottom) return { left, right, top, bottom };
        return null;
    };
    const cursorFor = ed =>
        ed.left && ed.top || ed.right && ed.bottom ? 'nwse-resize' :
        ed.right && ed.top || ed.left && ed.bottom ? 'nesw-resize' :
        ed.left || ed.right ? 'ew-resize' :
        'ns-resize';
    container.addEventListener('mousedown', e => {
        const ed = getEdges(e.clientX, e.clientY);
        if (ed) {
            startResize(e.clientX, e.clientY, ed);
            e.preventDefault();
        }
    });
    container.addEventListener('touchstart', e => {
        const t = e.touches[0];
        if (t) {
            const ed = getEdges(t.clientX, t.clientY);
            if (ed) {
                startResize(t.clientX, t.clientY, ed);
                e.preventDefault();
            }
        }
    }, { passive: false });
    container.addEventListener('mousemove', e => {
        if (resize) return;
        const ed = getEdges(e.clientX, e.clientY);
        container.style.cursor = ed ? cursorFor(ed) : '';
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

    const handleMove = (x, y) => {
        if (drag) {
            const vw = document.documentElement.clientWidth;
            const vh = document.documentElement.clientHeight;
            let l = x - offsetX;
            let t = y - offsetY;
            l = clamp(l, 0, vw - container.offsetWidth);
            t = clamp(t, 0, vh - container.offsetHeight);
            container.style.left = l + 'px';
            container.style.top = t + 'px';
        } else if (resize) {
            let w = startW;
            let h = startH;
            if (resize.right) w += x - startX;
            if (resize.bottom) h += y - startY;
            if (resize.left) w -= x - startX;
            if (resize.top) h -= y - startY;

            w = clamp(w, 320, 560);
            h = clamp(h, 260, 720);

            let l = startL;
            let t = startT;
            if (resize.left) l = startL + (startW - w);
            if (resize.top)  t = startT + (startH - h);
            const vw = document.documentElement.clientWidth;
            const vh = document.documentElement.clientHeight;
            l = clamp(l, 0, vw - w);
            t = clamp(t, 0, vh - h);

            container.style.width  = w + 'px';
            container.style.height = h + 'px';
            container.style.left   = l + 'px';
            container.style.top    = t + 'px';
        }
    };

    document.addEventListener('mousemove', e => handleMove(e.clientX, e.clientY));
    document.addEventListener('touchmove', e => {
        const t = e.touches[0];
        if (t) handleMove(t.clientX, t.clientY);
    }, { passive: false });

    const endAction = () => {
        if (drag) {
            drag = false;
            document.body.style.userSelect = '';
            savePos();
        }
        if (resize) {
            resize = null;
            document.body.style.userSelect = '';
            saveSize();
        }
        container.style.cursor = '';
    };
    document.addEventListener('mouseup', endAction);
    document.addEventListener('touchend', endAction);
});
