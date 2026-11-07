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
    const voiceToggle = root.querySelector("[data-assistant-voice-toggle]");
    const sidebarToggles = [...(section?.querySelectorAll("[data-assistant-toggle]") || [])];
    const voiceLaunchers = [...document.querySelectorAll("[data-assistant-voice-launch]")];
    const openButton = sidebarToggles.find((toggle) => toggle.hasAttribute("data-assistant-open"));
    if (!form || !input || !output || !button || !status || !body || !voiceToggle || !openButton) return false;

    root.dataset.eduturnosInitialized = "true";
    let activeRequestController = null;
    let requestSequence = 0;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let voiceRecognition = null;
    let voiceCallActive = false;
    let voiceCallBusy = false;
    let voiceCallRestartTimer = 0;
    const setStatus = (message) => {
        status.textContent = message;
    };
    const refreshSend = () => {
        button.disabled = input.disabled || !input.value.trim();
        voiceToggle.disabled = !SpeechRecognition;
        voiceToggle.setAttribute("aria-pressed", String(voiceCallActive));
        const label = voiceCallActive ? "Finalizar conversación por voz" : "Iniciar conversación por voz";
        voiceToggle.setAttribute("aria-label", label);
        voiceToggle.title = label;
    };

    const stopVoiceConversation = (message = "") => {
        voiceCallActive = false;
        voiceCallBusy = false;
        window.clearTimeout(voiceCallRestartTimer);
        if (voiceRecognition) {
            try {
                voiceRecognition.stop();
            } catch (error) {
                console.warn("No se pudo detener el reconocimiento de voz de EDUBOT.", error);
            }
            voiceRecognition = null;
        }
        window.speechSynthesis?.cancel();
        refreshSend();
        if (message) setStatus(message);
    };

    const speakResponse = (text) => new Promise((resolve) => {
        if (!window.speechSynthesis || !window.SpeechSynthesisUtterance) {
            resolve();
            return;
        }
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "es-CO";
        utterance.onend = resolve;
        utterance.onerror = resolve;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
    });

    const startVoiceRecognition = (conversation = false) => {
        if (!SpeechRecognition) {
            setStatus("Este navegador no permite reconocimiento de voz. Usa Ayuda EDUTURNOS para escribir tu pregunta.");
            return;
        }
        const recognition = new SpeechRecognition();
        voiceRecognition = recognition;
        recognition.lang = "es-CO";
        recognition.continuous = conversation;
        recognition.interimResults = false;
        recognition.onresult = (event) => {
            const transcript = [...event.results]
                .slice(event.resultIndex)
                .filter((result) => result.isFinal)
                .map((result) => result[0]?.transcript || "")
                .join(" ")
                .trim();
            if (!transcript) return;
            if (conversation) {
                voiceCallBusy = true;
                input.value = transcript;
                input.dispatchEvent(new Event("input", { bubbles: true }));
                recognition.stop();
                form.requestSubmit();
                return;
            }
        };
        recognition.onerror = (event) => {
            if (event.error === "not-allowed" || event.error === "service-not-allowed") {
                stopVoiceConversation("El navegador no permitió usar el micrófono.");
            } else if (event.error !== "aborted" && event.error !== "no-speech") {
                setStatus("No se pudo reconocer la voz. Inténtalo otra vez.");
            }
        };
        recognition.onend = () => {
            if (voiceRecognition === recognition) voiceRecognition = null;
            if (conversation && voiceCallActive && !voiceCallBusy) {
                voiceCallRestartTimer = window.setTimeout(() => startVoiceRecognition(true), 250);
            }
            refreshSend();
        };
        try {
            recognition.start();
            setStatus(conversation
                ? "Escuchando. Habla con EDUBOT; puedes finalizar la conversación cuando quieras."
                : "Escuchando…");
        } catch (error) {
            voiceRecognition = null;
            setStatus("No se pudo iniciar el micrófono. Revisa los permisos del navegador.");
            console.warn("No se pudo iniciar el reconocimiento de voz de EDUBOT.", error);
        }
    };

    const toggleVoiceConversation = () => {
        if (!SpeechRecognition) {
            setStatus("Este navegador no admite reconocimiento de voz. Usa el teclado o abre EDUTURNOS en Chrome.");
            return;
        }
        if (voiceCallActive) {
            stopVoiceConversation("Conversación por voz finalizada.");
            return;
        }
        voiceCallActive = true;
        voiceCallBusy = false;
        refreshSend();
        setStatus("Solicitando permiso para usar el micrófono…");
        if (!navigator.mediaDevices?.getUserMedia) {
            stopVoiceConversation("Este navegador no puede solicitar acceso al micrófono.");
            return;
        }
        navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
            stream.getTracks().forEach((track) => track.stop());
            if (voiceCallActive) startVoiceRecognition(true);
        }).catch((error) => {
            const message = error.name === "NotAllowedError" || error.name === "PermissionDeniedError"
                ? "No se concedió permiso al micrófono. Actívalo en los permisos del sitio y vuelve a intentarlo."
                : error.name === "NotFoundError" || error.name === "DevicesNotFoundError"
                    ? "No se encontró un micrófono disponible en este dispositivo."
                    : "No se pudo acceder al micrófono. Revisa los permisos del navegador.";
            stopVoiceConversation(message);
            console.warn("No se pudo solicitar acceso al micrófono de EDUBOT.", error);
        });
    };
    voiceToggle.disabled = !SpeechRecognition;
    voiceToggle.addEventListener("click", toggleVoiceConversation);

    const resetConversation = () => {
        stopVoiceConversation();
        requestSequence += 1;
        activeRequestController?.abort();
        activeRequestController = null;
        while (output.children.length > 1) output.lastElementChild.remove();
        output.scrollTop = 0;
        input.disabled = false;
        input.value = "";
        input.style.height = "";
        setStatus("");
        refreshSend();
    };

    const dragHandle = root.querySelector(".assistant-header");
    const resizeHandles = [...root.querySelectorAll("[data-assistant-resize]")];
    const chatPositionKey = "eduturnos-assistant-position-v1";
    let dragState = null;
    let resizeState = null;
    let defaultChatSize = null;

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

    const placeChatNearLauncher = (launcher) => {
        const anchor = launcher.getBoundingClientRect();
        const panel = root.getBoundingClientRect();
        const gap = 12;
        let left = anchor.left - panel.width - gap;
        if (left < 8) left = anchor.right + gap;
        let top = anchor.top + (anchor.height - panel.height) / 2;
        const maxTop = Math.max(8, window.innerHeight - panel.height - 8);
        if (top < 8) top = Math.min(maxTop, anchor.bottom + gap);
        if (top > maxTop) top = Math.max(8, anchor.top - panel.height - gap);
        placeChat(left, top);
    };

    const clearChatPosition = () => {
        root.style.removeProperty("left");
        root.style.removeProperty("top");
        root.style.removeProperty("right");
        root.style.removeProperty("bottom");
        root.style.removeProperty("transform");
        root.style.removeProperty("width");
        root.style.removeProperty("height");
        try {
            localStorage.removeItem(chatPositionKey);
        } catch {
            return;
        }
    };

    const resizeLimits = () => {
        const maxWidth = Math.max(1, Math.min(600, window.innerWidth - 16));
        const mobileViewport = window.innerWidth <= 900;
        const availableHeight = window.innerHeight - (mobileViewport ? 100 : 16);
        const maxHeight = Math.max(1, Math.min(700, availableHeight));
        return {
            minWidth: Math.min(defaultChatSize?.width ?? 260, maxWidth),
            maxWidth,
            minHeight: Math.min(defaultChatSize?.height ?? 280, maxHeight),
            maxHeight,
        };
    };

    root.addEventListener("pointerdown", (event) => {
        const handle = event.target instanceof Element
            ? event.target.closest("[data-assistant-resize]")
            : null;
        if (!handle || !event.isPrimary || event.button !== 0) return;
        const bounds = root.getBoundingClientRect();
        resizeState = {
            pointerId: event.pointerId,
            direction: handle.dataset.assistantResize,
            startX: event.clientX,
            startY: event.clientY,
            startWidth: bounds.width,
            startHeight: bounds.height,
            startLeft: bounds.left,
            startTop: bounds.top,
        };
        root.style.left = `${bounds.left}px`;
        root.style.top = `${bounds.top}px`;
        root.style.right = "auto";
        root.style.bottom = "auto";
        root.setPointerCapture(event.pointerId);
        root.classList.add("is-resizing");
        event.preventDefault();
    });

    root.addEventListener("pointermove", (event) => {
        if (!resizeState || event.pointerId !== resizeState.pointerId) return;
        const { direction, startX, startY, startWidth, startHeight, startLeft, startTop } = resizeState;
        const deltaX = event.clientX - startX;
        const deltaY = event.clientY - startY;
        const limits = resizeLimits();
        const growsLeft = direction.includes("w");
        const growsTop = direction.includes("n");
        const widthDelta = growsLeft ? -deltaX : deltaX;
        const heightDelta = growsTop ? -deltaY : deltaY;
        const fixedRight = startLeft + startWidth;
        const fixedBottom = startTop + startHeight;
        const maxWidth = limits.maxWidth;
        const maxHeight = limits.maxHeight;
        const width = Math.min(maxWidth, Math.max(Math.min(limits.minWidth, maxWidth), startWidth + widthDelta));
        const height = Math.min(maxHeight, Math.max(Math.min(limits.minHeight, maxHeight), startHeight + heightDelta));
        const left = growsLeft ? fixedRight - width : startLeft;
        const top = growsTop ? fixedBottom - height : startTop;

        root.style.width = `${width}px`;
        root.style.height = `${height}px`;
        root.style.left = `${Math.min(Math.max(8, left), window.innerWidth - width - 8)}px`;
        root.style.top = `${Math.min(Math.max(8, top), window.innerHeight - height - 8)}px`;
    });

    const finishResizing = (event) => {
        if (!resizeState || event.pointerId !== resizeState.pointerId) return;
        resizeState = null;
        root.classList.remove("is-resizing");
    };

    root.addEventListener("pointerup", finishResizing);
    root.addEventListener("pointercancel", finishResizing);

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

    const setChatOpen = (isOpen, sourceButton, voiceOnly = false) => {
        if (!isOpen) {
            resetConversation();
            clearChatPosition();
            defaultChatSize = null;
        } else if (!root.hidden && root.classList.contains("is-voice-mode") !== voiceOnly) {
            resetConversation();
        }
        root.hidden = !isOpen;
        root.classList.toggle("is-open", isOpen);
        root.classList.toggle("is-voice-mode", isOpen && voiceOnly);
        [...sidebarToggles, ...voiceLaunchers].forEach((toggle) => {
            toggle.setAttribute("aria-expanded", String(isOpen));
        });
        if (isOpen) {
            clearChatPosition();
            const defaultBounds = root.getBoundingClientRect();
            defaultChatSize = {
                width: defaultBounds.width,
                height: defaultBounds.height,
            };
            if (voiceOnly && sourceButton) placeChatNearLauncher(sourceButton);
            if (voiceOnly && !voiceCallActive) toggleVoiceConversation();
        } else {
            (sourceButton && !root.contains(sourceButton) ? sourceButton : openButton).focus();
        }
    };

    sidebarToggles.forEach((toggleButton) => {
        toggleButton.addEventListener("click", () => {
            setChatOpen(toggleButton.hasAttribute("data-assistant-open"), toggleButton);
        });
    });

    voiceLaunchers.forEach((launcher) => {
        launcher.addEventListener("click", () => {
            setChatOpen(true, launcher, true);
        });
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !root.hidden) {
            setChatOpen(false, null);
        }
    });

    refreshSend();

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (button.disabled || input.disabled) return;
        const message = input.value.trim();
        if (!message || message.length > 1200) return;

        const answerByVoice = voiceCallActive;
        button.disabled = true;
        input.disabled = true;
        setStatus("EDUBOT está preparando una respuesta…");
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
            let replyText = "";
            if (!response.ok) {
                answer.classList.add("assistant-error");
                answer.textContent = data && typeof data.error === "string"
                    ? data.error
                    : `El asistente respondió con un error (${response.status}).`;
                input.value = message;
            } else if (data && typeof data.respuesta === "string" && data.respuesta.trim()) {
                renderAssistantMarkdown(answer, data.respuesta);
                replyText = data.respuesta;
                if (data.accion === "crear_cita" && root.dataset.createCitationUrl) {
                    const actionLink = document.createElement("a");
                    actionLink.className = "assistant-action-link";
                    actionLink.href = root.dataset.createCitationUrl;
                    actionLink.textContent = root.dataset.createCitationLabel || "Abrir formulario de citación";
                    answer.append(actionLink);
                }
            } else {
                answer.textContent = "El asistente no devolvió una respuesta válida.";
                input.value = message;
            }
            output.append(answer);
            output.scrollTop = output.scrollHeight;
            if (answerByVoice && replyText) {
                await speakResponse(replyText);
            }
        } catch {
            if (controller.signal.aborted || currentRequest !== requestSequence) return;
            input.value = message;
            setStatus("No se pudo conectar con EDUTURNOS. Inténtalo nuevamente.");
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
                if (answerByVoice && voiceCallActive) {
                    voiceCallBusy = false;
                    voiceCallRestartTimer = window.setTimeout(() => {
                        if (voiceCallActive && !voiceRecognition) startVoiceRecognition(true);
                    }, 250);
                } else {
                    setStatus("");
                }
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
