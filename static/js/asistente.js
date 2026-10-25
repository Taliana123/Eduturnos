const initializeEduturnosAssistant = () => {
    const appendInlineMarkdown = (container, text) => {
        const tokenPattern = /(\*\*.+?\*\*|__.+?__|`[^`]+`|\*[^*\n]+\*)/g;
        let lastIndex = 0;

        for (const match of text.matchAll(tokenPattern)) {
            container.append(document.createTextNode(text.slice(lastIndex, match.index)));
            const token = match[0];
            const content = token.startsWith("**") || token.startsWith("__")
                ? token.slice(2, -2)
                : token.slice(1, -1);
            const element = document.createElement(token.startsWith("`") ? "code" : token.startsWith("*") && !token.startsWith("**") ? "em" : "strong");
            element.textContent = content;
            container.append(element);
            lastIndex = match.index + token.length;
        }
        container.append(document.createTextNode(text.slice(lastIndex)));
    };

    const renderAssistantMarkdown = (container, markdown) => {
        const lines = markdown.replace(/\r\n?/g, "\n").split("\n");
        const isTableRow = (line) => line.includes("|");
        const isTableSeparator = (line) => line.includes("-") && /^[\s|:-]+$/.test(line);
        const tableCells = (line) => line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
        let index = 0;

        while (index < lines.length) {
            const line = lines[index].trim();
            if (!line) {
                index += 1;
                continue;
            }

            if (index + 1 < lines.length && isTableRow(line) && isTableSeparator(lines[index + 1].trim())) {
                const wrapper = document.createElement("div");
                wrapper.className = "assistant-table-wrap";
                const table = document.createElement("table");
                const head = document.createElement("thead");
                const headerRow = document.createElement("tr");
                tableCells(line).forEach((cell) => {
                    const header = document.createElement("th");
                    appendInlineMarkdown(header, cell);
                    headerRow.append(header);
                });
                head.append(headerRow);
                table.append(head);
                const body = document.createElement("tbody");
                index += 2;
                while (index < lines.length && isTableRow(lines[index].trim())) {
                    const row = document.createElement("tr");
                    tableCells(lines[index].trim()).forEach((cell) => {
                        const dataCell = document.createElement("td");
                        appendInlineMarkdown(dataCell, cell);
                        row.append(dataCell);
                    });
                    body.append(row);
                    index += 1;
                }
                table.append(body);
                wrapper.append(table);
                container.append(wrapper);
                continue;
            }

            const heading = line.match(/^#{1,3}\s+(.+)$/);
            if (heading) {
                const element = document.createElement("strong");
                appendInlineMarkdown(element, heading[1]);
                container.append(element);
                index += 1;
                continue;
            }

            const listItem = line.match(/^(\s*)([-*+]|\d+[.)])\s+(.+)$/);
            if (listItem) {
                const ordered = /^\d/.test(listItem[2]);
                const list = document.createElement(ordered ? "ol" : "ul");
                while (index < lines.length) {
                    const item = lines[index].trim().match(/^([-*+]|\d+[.)])\s+(.+)$/);
                    if (!item || /^\d/.test(item[1]) !== ordered) break;
                    const element = document.createElement("li");
                    appendInlineMarkdown(element, item[2]);
                    list.append(element);
                    index += 1;
                }
                container.append(list);
                continue;
            }

            const paragraphLines = [line];
            index += 1;
            while (index < lines.length && lines[index].trim()) {
                const next = lines[index].trim();
                if (/^#{1,3}\s+/.test(next) || /^([-*+]|\d+[.)])\s+/.test(next)) break;
                if (index + 1 < lines.length && isTableRow(next) && isTableSeparator(lines[index + 1].trim())) break;
                paragraphLines.push(next);
                index += 1;
            }
            const paragraph = document.createElement("p");
            appendInlineMarkdown(paragraph, paragraphLines.join(" "));
            container.append(paragraph);
        }
    };

    const root = document.querySelector("[data-eduturnos-assistant]");
    if (!root) return false;

    const section = root.closest(".dashboard-help");
    if (root.dataset.eduturnosInitialized === "true") return true;

    const form = root.querySelector("form");
    const input = root.querySelector("textarea");
    const output = root.querySelector("[data-assistant-messages]");
    const button = form?.querySelector("button[type='submit']");
    const status = root.querySelector("[data-assistant-status]");
    const body = root.querySelector("[data-assistant-body]");
    const toggleButtons = [...(section?.querySelectorAll("[data-assistant-toggle]") || [])];
    const openButton = toggleButtons.find((toggle) => toggle.hasAttribute("data-assistant-open"));
    if (!form || !input || !output || !button || !status || !body || !openButton || !toggleButtons.length) return false;

    root.dataset.eduturnosInitialized = "true";
    let activeRequestController = null;
    let requestSequence = 0;
    const refreshSend = () => {
        button.disabled = input.disabled || !input.value.trim();
    };

    const resetConversation = () => {
        requestSequence += 1;
        activeRequestController?.abort();
        activeRequestController = null;
        while (output.children.length > 1) output.lastElementChild.remove();
        output.scrollTop = 0;
        input.disabled = false;
        input.value = "";
        input.style.height = "";
        status.textContent = "";
        refreshSend();
    };

    const dragHandle = root.querySelector(".assistant-header");
    const chatPositionKey = "eduturnos-assistant-position-v1";
    let dragState = null;

    const positionLimits = () => {
        const bounds = root.getBoundingClientRect();
        return {
            maxLeft: Math.max(8, window.innerWidth - bounds.width - 8),
            maxTop: Math.max(8, window.innerHeight - bounds.height - 8),
        };
    };

    const placeChat = (left, top) => {
        const limits = positionLimits();
        const clampedLeft = Math.min(Math.max(8, left), limits.maxLeft);
        const clampedTop = Math.min(Math.max(8, top), limits.maxTop);
        root.style.left = `${clampedLeft}px`;
        root.style.top = `${clampedTop}px`;
        root.style.right = "auto";
        root.style.bottom = "auto";
        root.style.transform = "none";
        return { left: clampedLeft, top: clampedTop, ...limits };
    };

    const clearChatPosition = () => {
        root.style.removeProperty("left");
        root.style.removeProperty("top");
        root.style.removeProperty("right");
        root.style.removeProperty("bottom");
        root.style.removeProperty("transform");
        try {
            localStorage.removeItem(chatPositionKey);
        } catch {
            return;
        }
    };

    dragHandle?.addEventListener("pointerdown", (event) => {
        if (!event.isPrimary || event.button !== 0 || event.target.closest("button")) return;
        const bounds = root.getBoundingClientRect();
        dragState = {
            pointerId: event.pointerId,
            offsetX: event.clientX - bounds.left,
            offsetY: event.clientY - bounds.top,
        };
        dragHandle.setPointerCapture(event.pointerId);
        root.classList.add("is-dragging");
        event.preventDefault();
    });

    dragHandle?.addEventListener("pointermove", (event) => {
        if (!dragState || event.pointerId !== dragState.pointerId) return;
        placeChat(event.clientX - dragState.offsetX, event.clientY - dragState.offsetY);
    });

    const finishDragging = (event) => {
        if (!dragState || event.pointerId !== dragState.pointerId) return;
        dragState = null;
        root.classList.remove("is-dragging");
    };

    dragHandle?.addEventListener("pointerup", finishDragging);
    dragHandle?.addEventListener("pointercancel", finishDragging);

    window.addEventListener("resize", () => {
        if (!root.hidden && root.style.left && root.style.top) {
            const bounds = root.getBoundingClientRect();
            placeChat(bounds.left, bounds.top);
        }
    });

    input.addEventListener("input", () => {
        refreshSend();
        input.style.height = "auto";
        input.style.height = `${Math.min(input.scrollHeight, 90)}px`;
    });

    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
            event.preventDefault();
            if (!button.disabled) form.requestSubmit();
        }
    });

    const setChatOpen = (isOpen, sourceButton) => {
        if (!isOpen) {
            resetConversation();
            clearChatPosition();
        }
        root.hidden = !isOpen;
        root.classList.toggle("is-open", isOpen);
        toggleButtons.forEach((toggle) => {
            toggle.setAttribute("aria-expanded", String(isOpen));
        });
        if (isOpen) {
            clearChatPosition();
        } else {
            (sourceButton?.hasAttribute("data-assistant-open") ? sourceButton : openButton).focus();
        }
    };

    toggleButtons.forEach((toggleButton) => {
        toggleButton.addEventListener("click", () => {
            setChatOpen(toggleButton.hasAttribute("data-assistant-open"), toggleButton);
        });
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !root.hidden) {
            setChatOpen(false, toggleButtons[0]);
        }
    });

    refreshSend();

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (button.disabled || input.disabled) return;
        const message = input.value.trim();
        if (!message || message.length > 1200) return;

        button.disabled = true;
        input.disabled = true;
        status.textContent = "EDUBOT está preparando una respuesta…";
        const controller = new AbortController();
        activeRequestController = controller;
        const currentRequest = ++requestSequence;

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
                signal: controller.signal,
            });
            if (currentRequest !== requestSequence) return;
            const data = await response.json().catch(() => null);
            if (currentRequest !== requestSequence) return;
            const answer = document.createElement("div");
            answer.className = "assistant-answer";
            if (!response.ok) {
                answer.classList.add("assistant-error");
                answer.textContent = data && typeof data.error === "string"
                    ? data.error
                    : `El asistente respondió con un error (${response.status}).`;
                input.value = message;
            } else if (data && typeof data.respuesta === "string" && data.respuesta.trim()) {
                renderAssistantMarkdown(answer, data.respuesta);
            } else {
                answer.textContent = "El asistente no devolvió una respuesta válida.";
                input.value = message;
            }
            output.append(answer);
            output.scrollTop = output.scrollHeight;
        } catch {
            if (controller.signal.aborted || currentRequest !== requestSequence) return;
            input.value = message;
            const answer = document.createElement("p");
            answer.className = "assistant-answer assistant-error";
            answer.textContent = "No se pudo conectar con EDUTURNOS. Inténtalo nuevamente.";
            output.append(answer);
            output.scrollTop = output.scrollHeight;
        } finally {
            if (currentRequest === requestSequence) {
                activeRequestController = null;
                input.disabled = false;
                refreshSend();
                status.textContent = "";
                input.focus();
            }
        }
    });

    return true;
};

const startEduturnosAssistant = () => {
    const synchronizeAssistant = () => {
        if (!initializeEduturnosAssistant()) return;

        const scope = document.querySelector(".dashboard-help");
        observer.disconnect();
        if (scope) observer.observe(scope, { childList: true, subtree: true });
    };
    const observer = new MutationObserver(synchronizeAssistant);

    observer.observe(document.documentElement, { childList: true, subtree: true });
    synchronizeAssistant();
};

startEduturnosAssistant();
