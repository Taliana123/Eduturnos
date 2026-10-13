document.addEventListener("DOMContentLoaded", () => {
    const root = document.querySelector("[data-eduturnos-assistant]");
    if (!root) return;

    const beepyFrame = root.querySelector('[data-beepy-frame]');
    if (beepyFrame) {
        let conversationSequence = 0;
        const startConversation = () => {
            const url = new URL(beepyFrame.dataset.src, location.href);
            conversationSequence += 1;
            url.searchParams.set('conversation', `${Date.now()}-${conversationSequence}`);
            beepyFrame.src = url.href;
        };
        root.addEventListener('toggle', () => {
            if (root.open && !beepyFrame.getAttribute('src')) startConversation();
        });
        root.querySelector('[data-beepy-restart]').addEventListener('click', startConversation);
        if (root.open) startConversation();
        root.querySelector('[data-beepy-close]').addEventListener('click', () => {
            root.open = false;
            root.querySelector('summary').focus();
        });
        return;
    }

    const form = root.querySelector("form");
    const input = root.querySelector("textarea");
    const output = root.querySelector("[data-assistant-messages]");
    if (!form || !input || !output) return;
    const button = form.querySelector("button[type='submit']");
    const status = root.querySelector("[data-assistant-status]");
    if (!button || !status) return;
    const panel = root.querySelector('.dashboard-assistant-panel');
    const clear = root.querySelector('[data-assistant-clear]');
    const expand = root.querySelector('[data-assistant-expand]');
    const greeting = output.querySelector('[data-assistant-greeting]').cloneNode(true);
    const refreshSend = () => { button.disabled = input.disabled || !input.value.trim(); };
    input.addEventListener('input', () => {
        refreshSend();
        input.style.height = 'auto';
        input.style.height = `${Math.min(input.scrollHeight, 120)}px`;
    });
    clear.addEventListener('click', () => {
        output.replaceChildren(greeting.cloneNode(true));
        input.value = '';
        status.textContent = '';
        refreshSend();
        if (!input.disabled) input.focus();
    });
    expand.addEventListener('click', () => {
        const expanded = panel.classList.toggle('assistant-expanded');
        expand.setAttribute('aria-pressed', String(expanded));
        expand.setAttribute('aria-label', expanded ? 'Reducir chat' : 'Ampliar chat');
        expand.title = expanded ? 'Reducir chat' : 'Ampliar chat';
    });
    root.querySelector('[data-assistant-close]').addEventListener('click', () => {
        root.open = false;
        root.querySelector('summary').focus();
    });
    input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
            event.preventDefault();
            if (!button.disabled) form.requestSubmit();
        }
    });
    refreshSend();

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (button.disabled) return;
        const message = input.value.trim();
        if (!message || message.length > 1200) return;

        button.disabled = true;
        clear.disabled = true;
        input.disabled = true;
        status.textContent = "Consultando…";
        const question = document.createElement("p");
        question.className = "assistant-question";
        question.textContent = message;
        output.append(question);
        output.scrollTop = output.scrollHeight;
        input.value = "";

        try {
            const response = await fetch(root.dataset.endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": root.dataset.csrf,
                },
                body: JSON.stringify({ mensaje: message }),
            });
            const data = await response.json();
            const answer = document.createElement("p");
            answer.className = "assistant-answer";
            answer.textContent = response.ok ? data.respuesta : (data.error || "No se pudo obtener respuesta.");
            output.append(answer);
            output.scrollTop = output.scrollHeight;
        } catch {
            const answer = document.createElement("p");
            answer.className = "assistant-answer";
            answer.textContent = "No se pudo conectar con el asistente. Inténtalo nuevamente.";
            output.append(answer);
            output.scrollTop = output.scrollHeight;
        } finally {
            input.disabled = false;
            clear.disabled = false;
            refreshSend();
            status.textContent = "";
            input.focus();
        }
    });
});
