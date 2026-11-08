const initializeEduturnosAssistant = () => {
    const spanishFemaleVoicePattern = /female|femenina|mujer|sabina|helena|laura|elena|m[oó]nica|paulina|luc[ií]a|isabella|zira|samantha|[#_]f\d/i;
    const selectSpanishVoice = () => {
        const voices = window.speechSynthesis?.getVoices() || [];
        const spanishVoices = voices.filter((voice) => /^es(?:-|_)/i.test(voice.lang));
        if (!spanishVoices.length) return null;
        return spanishVoices.find((voice) => /^es[-_]CO$/i.test(voice.lang) && spanishFemaleVoicePattern.test(voice.name))
            || spanishVoices.find((voice) => spanishFemaleVoicePattern.test(voice.name))
            || spanishVoices.find((voice) => /^es[-_]CO$/i.test(voice.lang))
            || spanishVoices[0];
    };
    const speakWithNativeVoice = (nativeVoice, text, onStart) => new Promise((resolve) => {
        if (!nativeVoice?.speak) {
            resolve(false);
            return;
        }

        let settled = false;
        let timeout = 0;
        const cleanup = () => {
            window.clearTimeout(timeout);
            window.removeEventListener("eduturnos-native-tts-start", handleStart);
            window.removeEventListener("eduturnos-native-tts-end", handleEnd);
            window.removeEventListener("eduturnos-native-tts-error", handleError);
        };
        const finish = (spoken) => {
            if (settled) return;
            settled = true;
            cleanup();
            resolve(spoken);
        };
        const handleStart = () => onStart?.();
        const handleEnd = () => finish(true);
        const handleError = () => finish(false);

        window.addEventListener("eduturnos-native-tts-start", handleStart);
        window.addEventListener("eduturnos-native-tts-end", handleEnd);
        window.addEventListener("eduturnos-native-tts-error", handleError);
        timeout = window.setTimeout(() => finish(false), 120000);
        try {
            nativeVoice.speak(text);
        } catch (error) {
            console.warn("No se pudo iniciar la voz nativa de EDUBOT.", error);
            finish(false);
        }
    });

    const enableCallPanelControls = (panel) => {
        const header = panel.querySelector(".assistant-voice-call__header");
        let initialSize = null;
        let dragState = null;
        let resizeState = null;

        const viewportLimits = () => ({
            maxWidth: Math.max(1, Math.min(640, window.innerWidth - 16)),
            maxHeight: Math.max(1, Math.min(760, window.innerHeight - 16)),
        });
        const constrainPosition = (left, top, width, height) => ({
            left: Math.min(Math.max(8, left), Math.max(8, window.innerWidth - width - 8)),
            top: Math.min(Math.max(8, top), Math.max(8, window.innerHeight - height - 8)),
        });
        const movePanel = (left, top) => {
            const bounds = panel.getBoundingClientRect();
            const position = constrainPosition(left, top, bounds.width, bounds.height);
            panel.style.left = `${position.left}px`;
            panel.style.top = `${position.top}px`;
            panel.style.right = "auto";
            panel.style.bottom = "auto";
        };
        const captureInitialSize = () => {
            if (initialSize || panel.hidden) return;
            const width = panel.offsetWidth;
            const height = panel.offsetHeight;
            if (width && height) initialSize = { width, height };
        };

        panel.addEventListener("pointerdown", (event) => {
            if (!event.isPrimary || (event.pointerType === "mouse" && event.button !== 0)) return;
            const target = event.target instanceof Element ? event.target : null;
            const resizeHandle = target?.closest("[data-assistant-call-resize]");
            if (resizeHandle) {
                const bounds = panel.getBoundingClientRect();
                captureInitialSize();
                resizeState = {
                    pointerId: event.pointerId,
                    direction: resizeHandle.dataset.assistantCallResize,
                    startX: event.clientX,
                    startY: event.clientY,
                    startWidth: bounds.width,
                    startHeight: bounds.height,
                    startLeft: bounds.left,
                    startTop: bounds.top,
                };
                panel.setPointerCapture(event.pointerId);
                panel.classList.add("is-resizing");
                event.preventDefault();
                return;
            }
            if (target?.closest("button, a, input, textarea, select, .assistant-voice-call__header")) return;
            const bounds = panel.getBoundingClientRect();
            const onRight = bounds.right - event.clientX <= 18;
            const onBottom = bounds.bottom - event.clientY <= 18;
            if (!onRight && !onBottom) return;
            captureInitialSize();
            resizeState = {
                pointerId: event.pointerId,
                direction: `${onBottom ? "s" : ""}${onRight ? "e" : ""}`,
                startX: event.clientX,
                startY: event.clientY,
                startWidth: bounds.width,
                startHeight: bounds.height,
                startLeft: bounds.left,
                startTop: bounds.top,
            };
            panel.setPointerCapture(event.pointerId);
            panel.classList.add("is-resizing");
            event.preventDefault();
        });

        header?.addEventListener("pointerdown", (event) => {
            if (!event.isPrimary || event.button !== 0 || event.target.closest("button")) return;
            const bounds = panel.getBoundingClientRect();
            dragState = {
                pointerId: event.pointerId,
                offsetX: event.clientX - bounds.left,
                offsetY: event.clientY - bounds.top,
            };
            header.setPointerCapture(event.pointerId);
            panel.classList.add("is-dragging");
            event.preventDefault();
        });

        panel.addEventListener("pointermove", (event) => {
            if (dragState && event.pointerId === dragState.pointerId) {
                movePanel(event.clientX - dragState.offsetX, event.clientY - dragState.offsetY);
                return;
            }
            if (!resizeState) {
                if (event.pointerType === "mouse") {
                    const bounds = panel.getBoundingClientRect();
                    const onRight = bounds.right - event.clientX <= 18;
                    const onBottom = bounds.bottom - event.clientY <= 18;
                    panel.style.cursor = onRight && onBottom ? "nwse-resize"
                        : onRight ? "ew-resize"
                            : onBottom ? "ns-resize"
                                : "";
                }
                return;
            }
            if (event.pointerId !== resizeState.pointerId) return;

            const { direction, startX, startY, startWidth, startHeight, startLeft, startTop } = resizeState;
            const limits = viewportLimits();
            const growsLeft = direction.includes("w");
            const growsTop = direction.includes("n");
            const widthDelta = growsLeft ? startX - event.clientX : event.clientX - startX;
            const heightDelta = growsTop ? startY - event.clientY : event.clientY - startY;
            const width = Math.min(limits.maxWidth, Math.max(Math.min(initialSize.width, limits.maxWidth), startWidth + widthDelta));
            const height = Math.min(limits.maxHeight, Math.max(Math.min(initialSize.height, limits.maxHeight), startHeight + heightDelta));
            const left = growsLeft ? startLeft + startWidth - width : startLeft;
            const top = growsTop ? startTop + startHeight - height : startTop;
            const position = constrainPosition(left, top, width, height);

            panel.style.width = `${width}px`;
            panel.style.height = `${height}px`;
            panel.style.left = `${position.left}px`;
            panel.style.top = `${position.top}px`;
            panel.style.right = "auto";
            panel.style.bottom = "auto";
        });

        const finishPointerAction = (event) => {
            if (dragState?.pointerId === event.pointerId) {
                dragState = null;
                panel.classList.remove("is-dragging");
            }
            if (resizeState?.pointerId === event.pointerId) {
                resizeState = null;
                panel.classList.remove("is-resizing");
            }
        };
        panel.addEventListener("pointerup", finishPointerAction);
        panel.addEventListener("pointercancel", finishPointerAction);
        window.addEventListener("resize", () => {
            if (panel.hidden) return;
            const bounds = panel.getBoundingClientRect();
            const limits = viewportLimits();
            const width = Math.min(bounds.width, limits.maxWidth);
            const height = Math.min(bounds.height, limits.maxHeight);
            const position = constrainPosition(bounds.left, bounds.top, width, height);
            panel.style.width = `${width}px`;
            panel.style.height = `${height}px`;
            panel.style.left = `${position.left}px`;
            panel.style.top = `${position.top}px`;
        });

        return { captureInitialSize };
    };

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

    const initializePublicAssistantVoice = () => {
        const panel = document.querySelector("[data-assistant-public-call]");
        const launchers = [...document.querySelectorAll("[data-assistant-voice-launch]")];
        if (!panel || !launchers.length || panel.dataset.initialized === "true") return false;

        const state = panel.querySelector("[data-assistant-public-state]");
        const speaker = panel.querySelector("[data-assistant-public-speaker]");
        const transcript = panel.querySelector("[data-assistant-public-transcript]");
        const wave = panel.querySelector("[data-assistant-public-wave]");
        const toggle = panel.querySelector("[data-assistant-public-toggle]");
        const close = panel.querySelector("[data-assistant-public-close]");
        const action = panel.querySelector("[data-assistant-public-action]");
        if (!state || !speaker || !transcript || !wave || !toggle || !close || !action) return false;

        panel.dataset.initialized = "true";
        document.body.append(panel);
        const panelControls = enableCallPanelControls(panel);
        const NativeVoice = window.EDUTURNOSNativeVoice;
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let active = false;
        let busy = false;
        let recognition = null;
        let restartTimer = 0;
        let isOpen = false;

        const setState = (message) => {
            state.textContent = message;
            wave.classList.toggle("is-active", active && !busy);
            wave.classList.toggle("is-speaking", busy);
            panel.classList.toggle("is-listening", active && !busy);
            panel.classList.toggle("is-speaking", busy);
            toggle.setAttribute("aria-pressed", String(active));
            action.textContent = active ? "Colgar" : panel.classList.contains("is-ended") ? "Llamada finalizada" : "Iniciar llamada";
        };
        const publicAnswer = (question) => {
            const text = question.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
            if (text.includes("contrasena") || text.includes("clave")) {
                return "En la pantalla de inicio de sesión, selecciona «Olvidé mi contraseña» y sigue las instrucciones que recibirás en tu correo.";
            }
            if (text.includes("cita") || text.includes("calendario")) {
                return "Para consultar o solicitar una cita, inicia sesión en EDUTURNOS. Las opciones disponibles dependen de tu perfil.";
            }
            if (text.includes("registro") || text.includes("cuenta") || text.includes("ingresar") || text.includes("iniciar sesion")) {
                return "Selecciona «Iniciar sesión» o «Crear cuenta» en la parte superior de la página. Si tu institución ya te registró, usa las credenciales que te entregaron.";
            }
            return "Puedo orientarte sobre el acceso, las contraseñas y las citas. Para ayuda personalizada, inicia sesión y abre EDUBOT.";
        };
        const answerByVoice = (question) => {
            busy = true;
            speaker.textContent = "EDUBOT";
            transcript.textContent = `Te escuché: ${question}`;
            const answer = publicAnswer(question);
            setState(answer);
            const finishSpeech = (message = "Escuchando…") => {
                if (!active) return;
                busy = false;
                speaker.textContent = "Tú";
                setState(message);
                restartTimer = window.setTimeout(startRecognition, 250);
            };
            const speakInBrowser = () => {
                if (!window.speechSynthesis || !window.SpeechSynthesisUtterance) {
                    finishSpeech("La respuesta está en pantalla, pero no hay una voz disponible en este dispositivo.");
                    return;
                }
                const utterance = new SpeechSynthesisUtterance(answer);
                utterance.lang = "es-CO";
                utterance.voice = selectSpanishVoice();
                utterance.onend = utterance.onerror = () => finishSpeech();
                window.speechSynthesis.cancel();
                window.speechSynthesis.speak(utterance);
            };
            if (NativeVoice?.speak) {
                speakWithNativeVoice(NativeVoice, answer, () => {
                    if (active) setState("EDUBOT está hablando…");
                }).then((spoken) => {
                    if (!active) return;
                    if (spoken) finishSpeech();
                    else speakInBrowser();
                });
                return;
            }
            speakInBrowser();
        };
        const startWebRecognition = () => {
            if (!active || !SpeechRecognition) return;
            recognition = new SpeechRecognition();
            recognition.lang = "es-CO";
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.onstart = () => setState("Micrófono activo. Habla ahora…");
            recognition.onspeechstart = () => setState("Te escucho…");
            recognition.onspeechend = () => setState("Procesando lo que dijiste…");
            recognition.onresult = (event) => {
                const results = [...event.results].slice(event.resultIndex);
                const heardText = results.map((result) => result[0]?.transcript || "").join(" ").trim();
                if (heardText) transcript.textContent = `Te escuché: ${heardText}`;
                const question = results
                    .filter((result) => result.isFinal)
                    .map((result) => result[0]?.transcript || "")
                    .join(" ")
                    .trim();
                if (!question) return;
                busy = true;
                recognition.stop();
                answerByVoice(question);
            };
            recognition.onerror = (event) => {
                if (!active) return;
                if (event.error === "not-allowed" || event.error === "service-not-allowed") {
                    stop("El navegador bloqueó el micrófono. Concede el permiso y vuelve a iniciar.");
                } else if (event.error === "audio-capture") {
                    stop("No se pudo iniciar el micrófono. Comprueba el dispositivo y sus permisos.");
                } else if (event.error === "no-speech") {
                    setState("No detecté voz. Habla ahora para que EDUBOT pueda escucharte.");
                } else if (event.error === "network") {
                    stop("El reconocimiento de voz no pudo conectarse. Comprueba tu conexión e inténtalo otra vez.");
                } else if (event.error !== "aborted") {
                    setState("No se pudo reconocer la voz. Inténtalo otra vez.");
                }
            };
            recognition.onend = () => {
                recognition = null;
                if (active && !busy) restartTimer = window.setTimeout(startRecognition, 500);
            };
            try {
                recognition.start();
                setState("Solicitando acceso al micrófono…");
            } catch (error) {
                stop("No se pudo iniciar el micrófono. Vuelve a intentarlo.");
                console.warn("No se pudo iniciar el micrófono de EDUBOT.", error);
            }
        };
        function startRecognition() {
            if (!active) return;
            if (NativeVoice?.startListening) {
                setState("Solicitando permiso para usar el micrófono…");
                try {
                    NativeVoice.startListening();
                } catch (error) {
                    stop("No se pudo iniciar el reconocimiento de voz en este dispositivo.");
                    console.error("No se pudo iniciar el reconocimiento nativo de EDUBOT.", error);
                }
            } else if (SpeechRecognition) {
                if (!window.isSecureContext) {
                    stop("El micrófono requiere una conexión segura. Abre EDUTURNOS con su dirección HTTPS.");
                    return;
                }
                setState("Solicitando acceso al micrófono…");
                startWebRecognition();
            } else {
                stop("El reconocimiento de voz no está disponible en este navegador. Abre EDUTURNOS en Chrome actualizado.");
            }
        }
        function stop(message = "Conversación por voz finalizada.") {
            active = false;
            busy = false;
            window.clearTimeout(restartTimer);
            if (NativeVoice?.stopListening) NativeVoice.stopListening();
            if (NativeVoice?.stopSpeaking) NativeVoice.stopSpeaking();
            if (recognition) {
                try {
                    recognition.stop();
                } catch (error) {
                    console.warn("No se pudo detener el micrófono de EDUBOT.", error);
                }
                recognition = null;
            }
            window.speechSynthesis?.cancel();
            speaker.textContent = "Tú";
            setState(message);
        }
        const positionPanel = (launcher) => {
            const anchor = launcher.getBoundingClientRect();
            const bounds = panel.getBoundingClientRect();
            const left = anchor.left - bounds.width - 14 >= 8
                ? anchor.left - bounds.width - 14
                : Math.min(anchor.right + 14, window.innerWidth - bounds.width - 8);
            panel.style.left = `${Math.max(8, left)}px`;
            panel.style.top = `${Math.max(8, Math.min(anchor.top, window.innerHeight - bounds.height - 8))}px`;
        };
        const closePanel = () => {
            stop("");
            isOpen = false;
            panel.hidden = true;
            panel.setAttribute("aria-hidden", "true");
            panel.classList.remove("is-open", "is-ended");
            launchers.forEach((launcher) => launcher.setAttribute("aria-expanded", "false"));
        };

        window.addEventListener("eduturnos-native-voice-ready", () => {
            if (active && !busy) setState("Micrófono activo. Habla ahora…");
        });
        window.addEventListener("eduturnos-native-voice-result", (event) => {
            const question = event.detail?.text?.trim();
            if (active && question) {
                transcript.textContent = `Te escuché: ${question}`;
                answerByVoice(question);
            }
        });
        window.addEventListener("eduturnos-native-voice-partial-result", (event) => {
            const text = event.detail?.text?.trim();
            if (active && text) transcript.textContent = `Te escuché: ${text}`;
        });
        window.addEventListener("eduturnos-native-voice-speech-start", () => {
            if (active && !busy) setState("Te escucho…");
        });
        window.addEventListener("eduturnos-native-voice-speech-end", () => {
            if (active && !busy) setState("Procesando lo que dijiste…");
        });
        window.addEventListener("eduturnos-native-voice-error", (event) => {
            if (!active) return;
            if (event.detail?.error === "no-speech") {
                setState("No te escuché. Inténtalo otra vez.");
            } else if (event.detail?.error === "not-allowed") {
                stop("Android bloqueó el micrófono. Concede el permiso a EDUTURNOS y vuelve a iniciar.");
            } else if (event.detail?.error === "unavailable") {
                stop("Android no encontró un servicio ni una aplicación para reconocer voz. Activa o instala la app de Google y vuelve a intentar.");
            } else if (event.detail?.error === "cancelled") {
                stop("Se canceló el reconocimiento de voz.");
            } else {
                stop("No hay un servicio de reconocimiento de voz disponible en este dispositivo.");
            }
        });
        window.addEventListener("eduturnos-native-voice-end", () => {
            if (active && !busy) restartTimer = window.setTimeout(startRecognition, 500);
        });
        launchers.forEach((launcher) => launcher.addEventListener("click", () => {
            if (isOpen) {
                closePanel();
                return;
            }
            isOpen = true;
            panel.hidden = false;
            panel.setAttribute("aria-hidden", "false");
            panel.classList.remove("is-ended");
            panel.classList.add("is-open");
            panelControls.captureInitialSize();
            positionPanel(launcher);
            launchers.forEach((item) => item.setAttribute("aria-expanded", "true"));
            active = true;
            startRecognition();
        }));
        close.addEventListener("click", closePanel);
        toggle.addEventListener("click", () => {
            if (active) {
                stop();
                panel.classList.add("is-ended");
            } else if (panel.classList.contains("is-ended")) {
                closePanel();
            } else {
                active = true;
                startRecognition();
            }
        });
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && isOpen) closePanel();
        });
        return true;
    };

    const root = document.querySelector("[data-eduturnos-assistant]");
    if (!root) return initializePublicAssistantVoice();

    const section = root.closest(".dashboard-help");
    if (root.dataset.eduturnosInitialized === "true") return true;

    const form = root.querySelector("form");
    const input = root.querySelector("textarea");
    const output = root.querySelector("[data-assistant-messages]");
    const button = form?.querySelector("button[type='submit']");
    const status = root.querySelector("[data-assistant-status]");
    const body = root.querySelector("[data-assistant-body]");
    const voiceToggle = root.querySelector("[data-assistant-voice-toggle]");
    const callPanel = section?.querySelector("[data-assistant-call]");
    const callState = callPanel?.querySelector("[data-assistant-call-state]");
    const callTranscript = callPanel?.querySelector("[data-assistant-call-transcript]");
    const callSpeaker = callPanel?.querySelector("[data-assistant-call-speaker]");
    const callToggle = callPanel?.querySelector("[data-assistant-call-toggle]");
    const callWave = callPanel?.querySelector("[data-assistant-call-wave]");
    const callClose = callPanel?.querySelector("[data-assistant-call-close]");
    const callAction = callPanel?.querySelector("[data-assistant-call-action]");
    const callActionLink = callPanel?.querySelector("[data-assistant-call-action-link]");
    const callConfirmAction = callPanel?.querySelector("[data-assistant-call-confirm]");
    const sidebarToggles = [...(section?.querySelectorAll("[data-assistant-toggle]") || [])];
    const voiceLaunchers = [...document.querySelectorAll("[data-assistant-voice-launch]")];
    const openButton = sidebarToggles.find((toggle) => toggle.hasAttribute("data-assistant-open"));
    if (!form || !input || !output || !button || !status || !body || !voiceToggle || !openButton
        || !callPanel || !callState || !callTranscript || !callSpeaker || !callToggle || !callWave || !callClose
        || !callAction || !callActionLink || !callConfirmAction) return false;

    root.dataset.eduturnosInitialized = "true";
    document.body.append(callPanel);
    const callPanelControls = enableCallPanelControls(callPanel);
    let activeRequestController = null;
    let requestSequence = 0;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const nativeVoice = window.EDUTURNOSNativeVoice;
    const canRecognizeVoice = Boolean(SpeechRecognition || nativeVoice?.startListening);
    let voiceRecognition = null;
    let voiceCallActive = false;
    let voiceCallBusy = false;
    let voiceCallRestartTimer = 0;
    let voiceCallOverlayOpen = false;
    let pendingCallCancellation = null;
    const setStatus = (message) => {
        status.textContent = message;
        callState.textContent = message || (voiceCallActive ? "Escuchando…" : "Listo para escucharte");
        callWave.classList.toggle("is-active", voiceCallActive && !voiceCallBusy);
        callWave.classList.toggle("is-speaking", voiceCallBusy);
        callPanel.classList.toggle("is-listening", voiceCallActive && !voiceCallBusy);
        callPanel.classList.toggle("is-speaking", voiceCallBusy);
        callToggle.setAttribute("aria-pressed", String(voiceCallActive));
        callToggle.setAttribute("aria-label", voiceCallActive ? "Finalizar conversación por voz" : "Iniciar conversación por voz");
        callAction.textContent = voiceCallActive
            ? "Colgar"
            : voiceCallOverlayOpen && callPanel.classList.contains("is-ended")
                ? "Llamada finalizada"
                : "Iniciar llamada";
    };
    const showVoiceMessage = (speaker, message) => {
        callSpeaker.textContent = speaker;
        callTranscript.textContent = `${speaker}: ${message}`;
    };
    const setCallPanelActionLink = (href, label) => {
        const actionUrl = new URL(href, window.location.origin);
        if (actionUrl.origin !== window.location.origin) return;
        callActionLink.href = actionUrl.href;
        callActionLink.textContent = label;
        callActionLink.hidden = false;
    };
    const submitCancellation = (actionUrl, citaId, confirmButton) => {
        if (!window.confirm(`¿Confirmas cancelar la cita #${citaId}? Se conservará en el historial.`)) return;
        confirmButton.disabled = true;
        const actionForm = document.createElement("form");
        actionForm.method = "post";
        actionForm.action = actionUrl;
        [["csrf_token", root.dataset.csrf], ["estado", "Cancelada"]].forEach(([name, value]) => {
            const field = document.createElement("input");
            field.type = "hidden";
            field.name = name;
            field.value = value;
            actionForm.append(field);
        });
        document.body.append(actionForm);
        actionForm.requestSubmit();
    };
    callConfirmAction.addEventListener("click", () => {
        if (!pendingCallCancellation) return;
        submitCancellation(
            pendingCallCancellation.actionUrl,
            pendingCallCancellation.citaId,
            callConfirmAction,
        );
    });
    const submitVoiceMessage = () => {
        if (typeof form.requestSubmit === "function") {
            form.requestSubmit();
        } else {
            form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
        }
    };
    const refreshSend = () => {
        button.disabled = input.disabled || !input.value.trim();
        voiceToggle.disabled = !canRecognizeVoice;
        voiceToggle.setAttribute("aria-pressed", String(voiceCallActive));
        const label = voiceCallActive ? "Finalizar conversación por voz" : "Iniciar conversación por voz";
        voiceToggle.setAttribute("aria-label", label);
        voiceToggle.title = label;
    };

    const stopVoiceConversation = (message = "") => {
        const wasActive = voiceCallActive;
        voiceCallActive = false;
        voiceCallBusy = false;
        window.clearTimeout(voiceCallRestartTimer);
        if (wasActive && nativeVoice?.stopListening) nativeVoice.stopListening();
        if (nativeVoice?.stopSpeaking) nativeVoice.stopSpeaking();
        if (voiceRecognition) {
            try {
                voiceRecognition.stop();
            } catch (error) {
                console.warn("No se pudo detener el reconocimiento de voz de EDUBOT.", error);
            }
            voiceRecognition = null;
        }
        window.speechSynthesis?.cancel();
        callSpeaker.textContent = "Tú";
        refreshSend();
        if (message) setStatus(message);
        else setStatus("");
    };

    const speakResponse = async (text) => {
        const onStart = () => {
            voiceCallBusy = true;
            callSpeaker.textContent = "EDUBOT";
            setStatus("EDUBOT está respondiendo…");
        };
        const onEnd = () => {
            voiceCallBusy = false;
            callSpeaker.textContent = "Tú";
        };

        if (nativeVoice?.speak) {
            const spoken = await speakWithNativeVoice(nativeVoice, text, onStart);
            if (spoken || !voiceCallActive) {
                onEnd();
                return;
            }
        }
        if (!window.speechSynthesis || !window.SpeechSynthesisUtterance) {
            onEnd();
            if (voiceCallActive) setStatus("EDUBOT respondió, pero no hay una voz disponible en este dispositivo.");
            return;
        }

        await new Promise((resolve) => {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "es-CO";
            utterance.voice = selectSpanishVoice();
            utterance.onstart = onStart;
            utterance.onend = utterance.onerror = () => {
                onEnd();
                resolve();
            };
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
        });
    };

    const startVoiceRecognition = (conversation = false) => {
        if (nativeVoice?.startListening) {
            setStatus("Solicitando acceso al micrófono…");
            try {
                nativeVoice.startListening();
            } catch (error) {
                stopVoiceConversation("No se pudo iniciar el reconocimiento de voz en este dispositivo.");
                console.warn("No se pudo iniciar el reconocimiento nativo de EDUBOT.", error);
            }
            return;
        }
        if (!SpeechRecognition) {
            setStatus("El reconocimiento de voz no está disponible en este navegador. Abre EDUTURNOS en Chrome actualizado.");
            return;
        }
        if (!window.isSecureContext) {
            stopVoiceConversation("El micrófono requiere una conexión segura. Abre EDUTURNOS con su dirección HTTPS.");
            return;
        }
        const recognition = new SpeechRecognition();
        voiceRecognition = recognition;
        recognition.lang = "es-CO";
        recognition.continuous = conversation;
        recognition.interimResults = true;
        recognition.onstart = () => setStatus("Micrófono activo. Habla ahora…");
        recognition.onspeechstart = () => setStatus("Te escucho…");
        recognition.onspeechend = () => setStatus("Procesando lo que dijiste…");
        recognition.onresult = (event) => {
            const results = [...event.results].slice(event.resultIndex);
            const heardText = results
                .map((result) => result[0]?.transcript || "")
                .join(" ")
                .trim();
            if (heardText) callTranscript.textContent = `Te escuché: ${heardText}`;
            const transcript = results
                .filter((result) => result.isFinal)
                .map((result) => result[0]?.transcript || "")
                .join(" ")
                .trim();
            if (!transcript) return;
            if (conversation) {
                voiceCallBusy = true;
                input.value = transcript;
                input.dispatchEvent(new Event("input", { bubbles: true }));
                setStatus("EDUBOT está preparando una respuesta…");
                recognition.stop();
                submitVoiceMessage();
                return;
            }
        };
        recognition.onerror = (event) => {
            if (event.error === "not-allowed" || event.error === "service-not-allowed") {
                stopVoiceConversation("El navegador bloqueó el micrófono. Revisa el permiso de EDUTURNOS y vuelve a iniciar.");
            } else if (event.error === "audio-capture") {
                stopVoiceConversation("No se pudo iniciar el micrófono. Comprueba el dispositivo y sus permisos.");
            } else if (event.error === "no-speech") {
                setStatus("No detecté voz. Habla ahora para que EDUBOT pueda escucharte.");
            } else if (event.error === "network") {
                stopVoiceConversation("El reconocimiento de voz no pudo conectarse. Comprueba tu conexión e inténtalo otra vez.");
            } else if (event.error !== "aborted") {
                setStatus("No se pudo reconocer la voz. Inténtalo otra vez.");
            }
        };
        recognition.onend = () => {
            if (voiceRecognition === recognition) voiceRecognition = null;
            if (conversation && voiceCallActive && !voiceCallBusy) {
                voiceCallRestartTimer = window.setTimeout(() => startVoiceRecognition(true), 500);
            }
            refreshSend();
        };
        try {
            recognition.start();
            setStatus("Solicitando acceso al micrófono…");
        } catch (error) {
            voiceRecognition = null;
            stopVoiceConversation("No se pudo iniciar el micrófono. Comprueba el permiso de EDUTURNOS y vuelve a intentar.");
            console.warn("No se pudo iniciar el reconocimiento de voz de EDUBOT.", error);
        }
    };

    window.addEventListener("eduturnos-native-voice-ready", () => {
        if (voiceCallActive && !voiceCallBusy) setStatus("Micrófono activo. Habla ahora…");
    });
    window.addEventListener("eduturnos-native-voice-result", (event) => {
        const transcript = event.detail?.text?.trim();
        if (!voiceCallActive || voiceCallBusy || !transcript) return;
        voiceCallBusy = true;
        showVoiceMessage("Tú", transcript);
        input.value = transcript;
        input.dispatchEvent(new Event("input", { bubbles: true }));
        setStatus("EDUBOT está preparando una respuesta…");
        submitVoiceMessage();
    });
    window.addEventListener("eduturnos-native-voice-partial-result", (event) => {
        const text = event.detail?.text?.trim();
        if (voiceCallActive && text) callTranscript.textContent = `Te escuché: ${text}`;
    });
    window.addEventListener("eduturnos-native-voice-speech-start", () => {
        if (voiceCallActive && !voiceCallBusy) setStatus("Te escucho…");
    });
    window.addEventListener("eduturnos-native-voice-speech-end", () => {
        if (voiceCallActive && !voiceCallBusy) setStatus("Procesando lo que dijiste…");
    });
    window.addEventListener("eduturnos-native-voice-error", (event) => {
        if (!voiceCallActive) return;
        const error = event.detail?.error;
        if (error === "no-speech") {
            setStatus("No te escuché. Inténtalo otra vez.");
            return;
        }
        const message = error === "not-allowed"
            ? "Android bloqueó el micrófono. Concede a EDUTURNOS el permiso de micrófono y vuelve a iniciar."
            : error === "unavailable"
                ? "Android no encontró un servicio ni una aplicación para reconocer voz. Activa o instala la app de Google y vuelve a intentar."
                : error === "cancelled"
                    ? "Se canceló el reconocimiento de voz."
                : "No se pudo reconocer la voz. Inténtalo otra vez.";
        stopVoiceConversation(message);
    });
    window.addEventListener("eduturnos-native-voice-end", () => {
        if (voiceCallActive && !voiceCallBusy) {
            voiceCallRestartTimer = window.setTimeout(() => startVoiceRecognition(true), 500);
        }
    });

    const toggleVoiceConversation = () => {
        if (!canRecognizeVoice) {
            setStatus("El reconocimiento de voz no está disponible en este navegador. Abre EDUTURNOS en Chrome actualizado.");
            return;
        }
        if (voiceCallActive) {
            stopVoiceConversation("Conversación por voz finalizada.");
            return;
        }
        voiceCallActive = true;
        voiceCallBusy = false;
        callTranscript.textContent = "";
        refreshSend();
        callSpeaker.textContent = "Tú";
        setStatus("Solicitando acceso al micrófono…");
        startVoiceRecognition(true);
    };
    voiceToggle.disabled = !canRecognizeVoice;
    voiceToggle.addEventListener("click", toggleVoiceConversation);
    callToggle.addEventListener("click", () => {
        if (voiceCallActive) {
            stopVoiceConversation("Llamada finalizada.");
            callToggle.setAttribute("aria-label", "Cerrar llamada");
            callToggle.querySelector("svg").innerHTML = "<path d=\"M6 6l12 12M18 6 6 18\"/>";
            callPanel.classList.add("is-ended");
            callAction.textContent = "Llamada finalizada";
        } else if (callPanel.classList.contains("is-ended")) {
            closeVoiceCall();
        } else {
            callPanel.classList.remove("is-ended");
            toggleVoiceConversation();
        }
    });

    const positionCallNearLauncher = (launcher) => {
        const anchor = launcher.getBoundingClientRect();
        const panel = callPanel.getBoundingClientRect();
        const gap = 14;
        const left = anchor.left - panel.width - gap >= 8
            ? anchor.left - panel.width - gap
            : Math.min(anchor.right + gap, window.innerWidth - panel.width - 8);
        const top = Math.min(
            Math.max(8, anchor.top + (anchor.height - panel.height) / 2),
            Math.max(8, window.innerHeight - panel.height - 8),
        );
        callPanel.style.left = `${Math.max(8, left)}px`;
        callPanel.style.top = `${top}px`;
    };

    const closeVoiceCall = () => {
        stopVoiceConversation();
        voiceCallOverlayOpen = false;
        callPanel.hidden = true;
        callPanel.setAttribute("aria-hidden", "true");
        callPanel.classList.remove("is-open", "is-ended");
        callActionLink.hidden = true;
        callConfirmAction.hidden = true;
        pendingCallCancellation = null;
        voiceLaunchers.forEach((launcher) => launcher.setAttribute("aria-expanded", "false"));
    };

    callClose.addEventListener("click", closeVoiceCall);

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

    const setChatOpen = (isOpen, sourceButton) => {
        if (!isOpen) {
            resetConversation();
            clearChatPosition();
            defaultChatSize = null;
        } else if (voiceCallOverlayOpen) {
            closeVoiceCall();
        }
        root.hidden = !isOpen;
        root.classList.toggle("is-open", isOpen);
        sidebarToggles.forEach((toggle) => {
            toggle.setAttribute("aria-expanded", String(isOpen));
        });
        if (isOpen) {
            clearChatPosition();
            const defaultBounds = root.getBoundingClientRect();
            defaultChatSize = {
                width: defaultBounds.width,
                height: defaultBounds.height,
            };
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
            if (voiceCallOverlayOpen) {
                closeVoiceCall();
                return;
            }
            if (!root.hidden) setChatOpen(false, launcher);
            voiceCallOverlayOpen = true;
            callPanel.hidden = false;
            callPanel.setAttribute("aria-hidden", "false");
            callPanel.classList.add("is-open");
            callPanel.classList.remove("is-ended");
            callActionLink.hidden = true;
            callConfirmAction.hidden = true;
            pendingCallCancellation = null;
            callPanelControls.captureInitialSize();
            callToggle.setAttribute("aria-label", "Finalizar conversación por voz");
            callToggle.innerHTML = "<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M4.6 14.2a12 12 0 0 1 14.8 0l-2.1 3.2a1.5 1.5 0 0 1-1.8.5l-2.1-.9a1.5 1.5 0 0 1-.9-1.4v-1a9 9 0 0 0-1 0v1a1.5 1.5 0 0 1-.9 1.4l-2.1.9a1.5 1.5 0 0 1-1.8-.5L4.6 14.2Z\"/></svg>";
            voiceLaunchers.forEach((item) => item.setAttribute("aria-expanded", "true"));
            positionCallNearLauncher(launcher);
            toggleVoiceConversation();
        });
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && voiceCallOverlayOpen) {
            closeVoiceCall();
        } else if (event.key === "Escape" && !root.hidden) {
            setChatOpen(false, null);
        }
    });

    refreshSend();

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (input.disabled || (button.disabled && !voiceCallActive)) return;
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
                if (answerByVoice) {
                    showVoiceMessage("EDUBOT", answer.textContent);
                    setStatus("No se pudo completar la solicitud.");
                    await speakResponse(answer.textContent);
                }
            } else if (data && typeof data.respuesta === "string" && data.respuesta.trim()) {
                renderAssistantMarkdown(answer, data.respuesta);
                replyText = data.respuesta;
                if (answerByVoice) showVoiceMessage("EDUBOT", replyText);
                if (data.accion === "crear_cita" && root.dataset.createCitationUrl) {
                    const actionLink = document.createElement("a");
                    actionLink.className = "assistant-action-link";
                    actionLink.href = root.dataset.createCitationUrl;
                    actionLink.textContent = root.dataset.createCitationLabel || "Abrir formulario de citación";
                    answer.append(actionLink);
                    if (voiceCallOverlayOpen) {
                        setCallPanelActionLink(actionLink.href, actionLink.textContent);
                    }
                } else if (data.accion === "confirmar_cancelacion") {
                    const actionUrl = new URL(data.accion_url, window.location.origin);
                    const citaId = Number(data.cita_id);
                    if (actionUrl.origin !== window.location.origin || !Number.isSafeInteger(citaId) || citaId < 1) {
                        answer.classList.add("assistant-error");
                        answer.append(document.createTextNode("No se pudo preparar una confirmación segura."));
                    } else {
                        pendingCallCancellation = { actionUrl: actionUrl.href, citaId };
                        callActionLink.hidden = true;
                        callConfirmAction.textContent = `Confirmar cancelación de cita #${citaId}`;
                        callConfirmAction.hidden = !voiceCallOverlayOpen;
                        const confirmButton = document.createElement("button");
                        confirmButton.className = "assistant-action-confirm";
                        confirmButton.type = "button";
                        confirmButton.textContent = `Confirmar cancelación de cita #${citaId}`;
                        confirmButton.addEventListener("click", () => submitCancellation(actionUrl.href, citaId, confirmButton));
                        answer.append(confirmButton);
                    }
                } else if (typeof data.accion_url === "string" && typeof data.accion_label === "string") {
                    const actionUrl = new URL(data.accion_url, window.location.origin);
                    if (actionUrl.origin === window.location.origin) {
                        const actionLink = document.createElement("a");
                        actionLink.className = "assistant-action-link";
                        actionLink.href = actionUrl.href;
                        actionLink.textContent = data.accion_label;
                        answer.append(actionLink);
                        if (voiceCallOverlayOpen) {
                            setCallPanelActionLink(actionLink.href, actionLink.textContent);
                        }
                    }
                }
            } else {
                answer.textContent = "El asistente no devolvió una respuesta válida.";
                input.value = message;
                if (answerByVoice) {
                    showVoiceMessage("EDUBOT", answer.textContent);
                    setStatus("No se recibió una respuesta válida.");
                    await speakResponse(answer.textContent);
                }
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
            if (answerByVoice) {
                const errorMessage = "No se pudo conectar con EDUTURNOS. Inténtalo nuevamente.";
                showVoiceMessage("EDUBOT", errorMessage);
                await speakResponse(errorMessage);
            }
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
                if (!answerByVoice) input.focus();
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
