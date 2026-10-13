document.addEventListener("DOMContentLoaded", () => {
	document.querySelectorAll(".sede-select").forEach((select) => {
		const output = select.parentElement.querySelector("[data-sede-code]");
		const sync = () => {
			const option = select.options[select.selectedIndex];
			if (output) output.textContent = option?.dataset?.codigo || "—";
		};
		select.addEventListener("change", sync);
		sync();
	});

	const mobileDialogMedia = window.matchMedia("(max-width: 900px)");
	const mobileNavToggle = document.querySelector("[data-mobile-nav-toggle]");
	const mobileNav = document.getElementById("eduturnos-mobile-nav");
	const mobileNavBackdrop = document.querySelector("[data-mobile-nav-backdrop]");
	if (mobileNavToggle && mobileNav && mobileNavBackdrop) {
		const setMobileNavOpen = (open) => {
			document.body.classList.toggle("mobile-nav-open", open);
			mobileNavToggle.setAttribute("aria-expanded", String(open));
			const label = open ? "Cerrar menú" : "Abrir menú";
			mobileNavToggle.setAttribute("aria-label", label);
			mobileNavToggle.title = label;
			mobileNavBackdrop.hidden = !open;
			if (open) mobileNav.querySelector("nav a")?.focus({ preventScroll: true });
			else mobileNavToggle.focus({ preventScroll: true });
		};
		mobileNavToggle.addEventListener("click", () => {
			setMobileNavOpen(mobileNavToggle.getAttribute("aria-expanded") !== "true");
		});
		mobileNavBackdrop.addEventListener("click", () => setMobileNavOpen(false));
		mobileNav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setMobileNavOpen(false)));
		document.addEventListener("keydown", (event) => {
			if (event.key === "Escape" && document.body.classList.contains("mobile-nav-open")) setMobileNavOpen(false);
		});
		mobileDialogMedia.addEventListener("change", () => {
			if (!mobileDialogMedia.matches && document.body.classList.contains("mobile-nav-open")) setMobileNavOpen(false);
		});
	}
	const assistantWidget = document.querySelector('[data-eduturnos-assistant]');
	const sidebarNavigation = document.querySelector('.eduturnos-desktop-sidebar > nav');
	if (assistantWidget && sidebarNavigation) {
		const originalParent = assistantWidget.parentNode;
		const originalNext = assistantWidget.nextSibling;
		const updateAssistantLocation = () => {
			if (mobileDialogMedia.matches) {
				if (assistantWidget.parentNode !== originalParent) originalParent.insertBefore(assistantWidget, originalNext);
			} else {
				sidebarNavigation.after(assistantWidget);
			}
		};
		updateAssistantLocation();
		mobileDialogMedia.addEventListener('change', updateAssistantLocation);
	}
	const citationsView = document.querySelector('.citas-desktop-view');
	if (citationsView) {
		const tabs = [...citationsView.querySelectorAll('[data-citas-state]')];
		const search = citationsView.querySelector('[data-citas-search]');
		const status = citationsView.querySelector('[data-citas-status]');
		let selectedState = '';
		const filterCitations = () => {
			let visible = 0;
			citationsView.querySelectorAll('[data-citas-row]').forEach((row) => {
				row.hidden = !row.dataset.student.toLocaleLowerCase().includes(search.value.trim().toLocaleLowerCase()) || (selectedState && row.dataset.state !== selectedState) || (status.value && row.dataset.state !== status.value);
				if (!row.hidden) visible++;
			});
			citationsView.querySelector('[data-citas-empty]').hidden = visible > 0;
		};
		const selectTab = (tab) => {
			selectedState = tab.dataset.citasState;
			tabs.forEach((button) => { button.setAttribute('aria-selected', String(button === tab)); button.tabIndex = button === tab ? 0 : -1; });
			filterCitations();
		};
		tabs.forEach((tab, index) => {
			tab.addEventListener('click', () => selectTab(tab));
			tab.addEventListener('keydown', (event) => {
				if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
				event.preventDefault();
				const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
				selectTab(tabs[next]); tabs[next].focus();
			});
		});
		search.addEventListener('input', filterCitations);
		status.addEventListener('change', () => selectTab(tabs[0]));
	}
	const administration = document.querySelector(".administracion-page .configuracion-page");
	if (administration) {
		const panels = [...administration.querySelectorAll(":scope > .panel, :scope > .grid > .panel")];
		if (panels.length) {
		const tabs = document.createElement("div");
		tabs.className = "admin-catalog-tabs";
		tabs.setAttribute("role", "tablist");
		tabs.setAttribute("aria-label", "Catálogos institucionales");
		let selected = 0;
		const updateCatalogs = () => {
			tabs.hidden = false;
			panels.forEach((panel, index) => {
				panel.hidden = index !== selected;
				const button = tabs.children[index];
				button.setAttribute("aria-selected", String(index === selected));
				button.tabIndex = index === selected ? 0 : -1;
				panel.setAttribute("role", "tabpanel");
				panel.setAttribute("aria-labelledby", button.id);
			});
		};
		panels.forEach((panel, index) => {
			panel.id = `admin-catalog-${index}`;
			const button = document.createElement("button");
			button.type = "button";
			button.id = `admin-tab-${index}`;
			button.textContent = panel.querySelector("h2").textContent;
			button.setAttribute("role", "tab");
			button.setAttribute("aria-controls", panel.id);
			panel.setAttribute("role", "tabpanel");
			panel.setAttribute("aria-labelledby", button.id);
			button.addEventListener("click", () => { selected = index; updateCatalogs(); });
			button.addEventListener("keydown", (event) => {
				if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
				event.preventDefault();
				selected = event.key === "Home" ? 0 : event.key === "End" ? panels.length - 1 : (selected + (event.key === "ArrowRight" ? 1 : -1) + panels.length) % panels.length;
				updateCatalogs();
				tabs.children[selected].focus();
			});
			tabs.append(button);
		});
		administration.querySelector(".page-head").after(tabs);
		updateCatalogs();
		}
	}
	document.addEventListener("click", (event) => {
		if (!(event.target instanceof Element)) return;
		const trigger = event.target.closest("[data-seguimiento-dialog]");
		if (trigger && !mobileDialogMedia.matches) {
			const detail = document.getElementById(trigger.dataset.seguimientoDialog);
			if (detail instanceof HTMLDialogElement) {
				event.preventDefault();
				if (!detail.open) detail.showModal();
			}
		}
		const detail = event.target.closest("dialog.seguimiento-detail-dialog");
		if (!(detail instanceof HTMLDialogElement)) return;
		if (event.target.closest("[data-seguimiento-close]")) detail.close();
		if (event.target.closest("[data-seguimiento-print]")) {
			document.body.classList.add("printing-seguimiento");
			window.print();
		}
		if (event.target === detail) {
			const bounds = detail.getBoundingClientRect();
			if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) detail.close();
		}
	});
	window.addEventListener("afterprint", () => {
		document.body.classList.remove("printing-seguimiento", "printing-cita");
		document.querySelector('.cita-print-document')?.remove();
	});
	const inlineIllustrations = [
		{ page: ".dashboard-page", heading: ".dashboard-head", art: ".dashboard-left-art" },
		{ page: ".registro-layout", heading: ".registro-encabezado", art: ".registro-ilustracion" },
	].flatMap((selectors) => {
		const container = document.querySelector(selectors.page);
		const art = container?.querySelector(selectors.art);
		const heading = container?.querySelector(selectors.heading);
		return art && heading ? [{ art, heading, parent: art.parentNode, next: art.nextElementSibling }] : [];
	});
	const updateInlineIllustrations = () => {
		inlineIllustrations.forEach(({ art, heading, parent, next }) => {
			if (mobileDialogMedia.matches) {
				if (art.parentNode !== heading) heading.append(art);
			} else if (art.parentNode !== parent) {
				parent.insertBefore(art, next);
			}
		});
	};
	updateInlineIllustrations();
	mobileDialogMedia.addEventListener("change", updateInlineIllustrations);
	window.addEventListener("resize", updateInlineIllustrations);
	const updateMobileFormFields = () => {
		document.querySelectorAll("[data-mobile-only]").forEach((input) => {
			input.disabled = !mobileDialogMedia.matches;
		});
	};
	updateMobileFormFields();
	const enhancePasswordFields = () => {
		document.querySelectorAll('input[type="password"]').forEach((input, index) => {
			if (input.closest(".password-field")) return;
			const addedAriaLabel = !input.hasAttribute("aria-label") && !input.hasAttribute("aria-labelledby") && !!input.labels?.[0];
			if (addedAriaLabel) input.setAttribute("aria-label", input.labels[0].textContent.trim().replace(/\s+/g, " "));
			if (!input.id) input.id = `eduturnos-password-${index}`;
			const wrapper = document.createElement("span");
			wrapper.className = "password-field";
			input.before(wrapper);
			wrapper.append(input);
			const button = document.createElement("button");
			button.type = "button";
			button.className = "password-toggle";
			button.setAttribute("aria-controls", input.id);
			button.setAttribute("aria-pressed", "false");
			const icon = document.createElement("img");
			icon.alt = "";
			icon.width = 18;
			icon.height = 18;
			button.append(icon);
			const hint = document.createElement("small");
			hint.className = "password-caps-hint";
			hint.textContent = "Bloq Mayús activado";
			hint.setAttribute("role", "status");
			hint.hidden = true;
			const refresh = () => {
				const empty = input.value.length === 0;
				button.hidden = empty;
				button.disabled = empty;
				if (empty) input.type = "password";
				const visible = input.type === "text";
				const label = visible ? "Ocultar contraseña" : "Mostrar contraseña";
				button.setAttribute("aria-label", label);
				button.setAttribute("aria-pressed", String(visible));
				button.title = label;
				icon.src = visible ? "/static/icons/lucide-eye-off.svg" : "/static/icons/lucide-eye.svg";
			};
			button.addEventListener("click", () => {
				input.type = input.type === "password" ? "text" : "password";
				refresh();
				input.focus({ preventScroll: true });
			});
			const updateCaps = (event) => {
				hint.hidden = !event.getModifierState("CapsLock");
			};
			input.addEventListener("keydown", updateCaps);
			input.addEventListener("keyup", updateCaps);
			input.addEventListener("input", refresh);
			input.addEventListener("change", refresh);
			input.addEventListener("focus", refresh);
			input.form?.addEventListener("reset", () => requestAnimationFrame(refresh));
			input.addEventListener("blur", () => { hint.hidden = true; });
			wrapper.append(button);
			wrapper.after(hint);
			refresh();
		});
	};
	enhancePasswordFields();
	const activateCitaTab = (dialog, selected) => {
		dialog.querySelectorAll("[data-cita-tab]").forEach((tab) => {
			const active = tab.dataset.citaTab === selected;
			tab.setAttribute("aria-selected", String(active));
			tab.tabIndex = active ? 0 : -1;
		});
		dialog.querySelectorAll("[data-cita-panel]").forEach((panel) => {
			panel.hidden = panel.dataset.citaPanel !== selected;
		});
	};
	const updateNoteForm = (form) => {
		const input = form.querySelector('textarea[name="nota"]');
		const button = form.querySelector('button[type="submit"]');
		const count = form.querySelector(".cita-note-count");
		if (!input || !button) return;
		button.disabled = !input.value.trim();
		button.textContent = "Guardar nota";
		if (count) count.textContent = `${input.value.length} / ${input.maxLength}`;
	};
	document.querySelectorAll(".cita-notes-form").forEach((form) => {
		updateNoteForm(form);
		form.addEventListener("input", () => updateNoteForm(form));
		form.addEventListener("submit", () => {
			const button = form.querySelector('button[type="submit"]');
			button.disabled = true;
			button.textContent = "Guardando...";
		});
	});
	window.addEventListener("pageshow", () => {
		document.querySelectorAll(".cita-notes-form").forEach(updateNoteForm);
	});
	const legacyMobilePage = document.querySelector("[data-mobile-cita-url]");
	if (mobileDialogMedia.matches && legacyMobilePage) {
		window.location.replace(legacyMobilePage.dataset.mobileCitaUrl);
		return;
	}
	const openMobileDialogFromHash = () => {
		if (!mobileDialogMedia.matches) return;
		const dialog = document.getElementById(window.location.hash.slice(1));
		if (dialog instanceof HTMLDialogElement && dialog.classList.contains("mobile-record-dialog") && !dialog.open) {
			if (dialog.querySelector('[data-cita-tab="notas"]')) activateCitaTab(dialog, "notas");
			dialog.showModal();
		}
	};
	document.addEventListener("click", (event) => {
		if (!(event.target instanceof Element)) return;
		const tab = event.target.closest("[data-cita-tab]");
		if (tab && (mobileDialogMedia.matches || tab.closest('.desktop-cita-open'))) {
			const tabDialog = tab.closest("dialog");
			if (tabDialog) activateCitaTab(tabDialog, tab.dataset.citaTab);
		}
		const trigger = event.target.closest("[data-mobile-dialog]");
		const desktopTrigger = event.target.closest('[data-desktop-cita-dialog]');
		if (desktopTrigger && !mobileDialogMedia.matches) {
			const detail = document.getElementById(desktopTrigger.dataset.desktopCitaDialog);
			if (detail instanceof HTMLDialogElement) {
				desktopTrigger.closest('dialog[open]')?.close();
				event.preventDefault(); detail.classList.add('desktop-cita-open');
				activateCitaTab(detail, 'info'); if (!detail.open) detail.showModal();
			}
		}
		if (trigger && mobileDialogMedia.matches) {
			const dialog = document.getElementById(trigger.dataset.mobileDialog);
			if (dialog instanceof HTMLDialogElement) {
				event.preventDefault();
				if (dialog.querySelector('[data-cita-tab="info"]')) activateCitaTab(dialog, "info");
				if (!dialog.open) dialog.showModal();
			}
		}
		const closeButton = event.target.closest("[data-mobile-dialog-close]");
		if (event.target.closest('[data-cita-print]')) {
			const content = event.target.closest('dialog')?.querySelector('[data-cita-print-content]');
			if (content) {
				document.querySelector('.cita-print-document')?.remove();
				const sheet = content.cloneNode(true);
				sheet.className = 'cita-print-document';
				sheet.removeAttribute('data-cita-print-content');
				document.body.append(sheet);
				document.body.classList.add('printing-cita');
				try { window.print(); } catch (error) {
					document.body.classList.remove('printing-cita'); sheet.remove(); throw error;
				}
			}
		}
		const dialog = closeButton?.closest("dialog.mobile-record-dialog");
		if (dialog instanceof HTMLDialogElement) dialog.close();
		if (event.target instanceof HTMLDialogElement && event.target.classList.contains("mobile-record-dialog")) {
			const bounds = event.target.getBoundingClientRect();
			if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) {
				event.target.close();
			}
		}
	});
	document.addEventListener("keydown", (event) => {
		if (event.target instanceof Element && event.target.matches("[data-cita-tab]") && (mobileDialogMedia.matches || event.target.closest('.desktop-cita-open'))) {
			const keys = ["ArrowLeft", "ArrowRight", "Home", "End"];
			if (keys.includes(event.key)) {
				event.preventDefault();
				const dialog = event.target.closest("dialog");
				const tabs = [...dialog.querySelectorAll("[data-cita-tab]")];
				const current = tabs.indexOf(event.target);
				const next = event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1 : (current + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
				activateCitaTab(dialog, tabs[next].dataset.citaTab);
				tabs[next].focus();
			}
		}
		if (event.key === "Escape" && mobileDialogMedia.matches) {
			const dialog = document.querySelector("dialog.mobile-record-dialog[open]");
			if (dialog instanceof HTMLDialogElement) {
				event.preventDefault();
				dialog.close();
			}
		}
	});
	mobileDialogMedia.addEventListener("change", () => {
		updateMobileFormFields();
		if (!mobileDialogMedia.matches) {
			document.querySelectorAll("dialog.mobile-record-dialog[open]").forEach((dialog) => dialog.close());
		} else {
			enhancePasswordFields();
			openMobileDialogFromHash();
		}
	});
	window.addEventListener("hashchange", openMobileDialogFromHash);
	openMobileDialogFromHash();
});

if ("serviceWorker" in navigator) {
	window.addEventListener("load", () => {
		navigator.serviceWorker.register("/service-worker.js");
	});
}
