import { createAvatar, createPartPreview, getPartsForSlot } from "@humation/core";
import { humation1 } from "@humation/assets-humation-1";

const slots = [
  ["head", "Cabello y cabeza"],
  ["body", "Ropa superior"],
  ["bottom", "Ropa inferior"],
  ["item", "Accesorios"],
  ["glasses", "Gafas"],
];
const colorSlots = [
  ["hair", "Cabello"],
  ["skin", "Piel"],
  ["clothes", "Ropa superior"],
  ["bottom", "Ropa inferior"],
  ["stroke", "Contorno"],
];
const genders = [
  ["mujer", "Mujer"],
  ["hombre", "Hombre"],
  ["nina", "Niña"],
  ["nino", "Niño"],
];
const fallbackColors = {
  hair: "#4A3728",
  skin: "#F4C9A8",
  clothes: "#6C91C2",
  bottom: "#52758A",
  stroke: "#302C36",
};

const cloneState = (state) => ({
  seed: state.seed,
  gender: state.gender || null,
  selections: { ...state.selections },
  colors: { ...state.colors },
  background: state.background,
});

const initialize = () => {
  const dialog = document.querySelector("#avatar-customizer");
  if (!dialog) return;

  const triggers = [...document.querySelectorAll("[data-avatar-open]")];
  const firstTrigger = triggers[0];
  const form = dialog.querySelector("[data-avatar-form]");
  const fields = dialog.querySelector("[data-avatar-fields]");
  const status = dialog.querySelector("[data-avatar-status]");
  const saveButton = dialog.querySelector("[data-avatar-save]");
  if (!firstTrigger || !form || !fields || !status || !saveButton) return;

  const userId = firstTrigger.dataset.avatarUser;
  const originalState = JSON.parse(firstTrigger.dataset.avatarConfig);
  let savedState = cloneState(originalState);
  let currentState = cloneState(originalState);
  const csrfToken = form.querySelector('input[name="csrf_token"]').value;

  const render = (state) => {
    currentState = cloneState(state);
    const source = createAvatar(humation1, {
      seed: currentState.seed,
      selections: currentState.selections,
      colors: currentState.colors,
      background: currentState.background,
      crop: "avatar",
    }).toDataUri();

    document.querySelectorAll("[data-avatar-image]").forEach((image) => {
      if (image.dataset.avatarUser !== userId) return;
      image.src = source;
    });
    dialog.querySelectorAll("[data-avatar-preview-image]").forEach((image) => {
      image.src = source;
    });
    fields.querySelectorAll("[data-avatar-choice]").forEach((choice) => {
      choice.setAttribute(
        "aria-pressed",
        String(currentState.selections[choice.dataset.avatarSlot] === choice.dataset.avatarPart),
      );
    });
    fields.querySelectorAll("[data-avatar-color]").forEach((input) => {
      input.value = currentState.colors[input.dataset.avatarColor] || fallbackColors[input.dataset.avatarColor];
    });
    const transparent = currentState.background === "transparent";
    fields.querySelectorAll("[data-avatar-gender-choice]").forEach((choice) => {
      choice.setAttribute("aria-pressed", String(currentState.gender === choice.dataset.avatarGenderChoice));
    });
    const backgroundToggle = fields.querySelector("[data-avatar-transparent]");
    const backgroundInput = fields.querySelector("[data-avatar-background]");
    if (backgroundToggle) backgroundToggle.checked = transparent;
    if (backgroundInput) {
      backgroundInput.disabled = transparent;
      backgroundInput.value = transparent ? "#F6F5F4" : currentState.background;
    }

    fields.querySelectorAll("[data-avatar-choice-preview]").forEach((image) => {
      const slot = image.dataset.avatarSlot;
      const part = getPartsForSlot(humation1, slot).find((candidate) => candidate.id === image.dataset.avatarPart);
      if (part) {
        image.src = createPartPreview(humation1, part, {
          colors: currentState.colors,
          background: "transparent",
        }).toDataUri();
      }
    });
  };

  const populateParts = () => {
    const genderGroup = document.createElement("fieldset");
    genderGroup.className = "avatar-option-group avatar-gender-group";
    const genderLegend = document.createElement("legend");
    genderLegend.textContent = "Género del personaje";
    genderGroup.append(genderLegend);
    const genderOptions = document.createElement("div");
    genderOptions.className = "avatar-gender-options";
    genderOptions.setAttribute("role", "group");
    genderOptions.setAttribute("aria-label", "Género del personaje");
    for (const [value, label] of genders) {
      const option = document.createElement("button");
      option.type = "button";
      option.className = "avatar-gender-choice";
      option.dataset.avatarGenderChoice = value;
      option.setAttribute("aria-pressed", "false");
      option.textContent = label;
      genderOptions.append(option);
    }
    const genderHint = document.createElement("small");
    genderHint.textContent = "El género se guarda como preferencia; cabello, ropa y rasgos se personalizan por separado.";
    genderGroup.append(genderOptions, genderHint);
    fields.append(genderGroup);

    for (const [slot, title] of slots) {
      const group = document.createElement("details");
      group.className = "avatar-option-group";
      const summary = document.createElement("summary");
      summary.textContent = title;
      group.append(summary);
      const grid = document.createElement("div");
      grid.className = "avatar-choice-grid";

      for (const part of getPartsForSlot(humation1, slot)) {
        const choice = document.createElement("button");
        choice.type = "button";
        choice.className = "avatar-choice";
        choice.dataset.avatarChoice = "";
        choice.dataset.avatarSlot = slot;
        choice.dataset.avatarPart = part.id;
        choice.setAttribute("aria-label", `${title}: ${part.name}`);
        choice.setAttribute("aria-pressed", "false");
        const preview = document.createElement("img");
        preview.alt = "";
        preview.loading = "lazy";
        preview.dataset.avatarChoicePreview = "";
        preview.dataset.avatarSlot = slot;
        preview.dataset.avatarPart = part.id;
        const label = document.createElement("span");
        label.textContent = part.name.replaceAll("-", " ");
        choice.append(preview, label);
        grid.append(choice);
      }
      group.append(grid);
      fields.append(group);
    }

    const colorsGroup = document.createElement("details");
    colorsGroup.className = "avatar-option-group avatar-color-group";
    const colorsSummary = document.createElement("summary");
    colorsSummary.textContent = "Colores";
    colorsGroup.append(colorsSummary);
    const colorGrid = document.createElement("div");
    colorGrid.className = "avatar-color-grid";
    for (const [slot, title] of colorSlots) {
      const label = document.createElement("label");
      label.className = "avatar-color-choice";
      label.textContent = title;
      const input = document.createElement("input");
      input.type = "color";
      input.dataset.avatarColor = slot;
      input.setAttribute("aria-label", `Color de ${title.toLocaleLowerCase("es")}`);
      label.append(input);
      colorGrid.append(label);
    }
    const backgroundLabel = document.createElement("label");
    backgroundLabel.className = "avatar-color-choice";
    backgroundLabel.textContent = "Fondo";
    const backgroundInput = document.createElement("input");
    backgroundInput.type = "color";
    backgroundInput.dataset.avatarBackground = "";
    backgroundLabel.append(backgroundInput);
    colorGrid.append(backgroundLabel);
    const transparentLabel = document.createElement("label");
    transparentLabel.className = "avatar-transparent-choice";
    const transparentToggle = document.createElement("input");
    transparentToggle.type = "checkbox";
    transparentToggle.dataset.avatarTransparent = "";
    transparentLabel.append(transparentToggle, document.createTextNode("Fondo transparente"));
    colorsGroup.append(colorGrid, transparentLabel);
    fields.append(colorsGroup);
  };

  const saveToServer = async (state) => {
    const response = await fetch(form.dataset.avatarSaveUrl, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(state),
    });
    const result = await response.json();
    if (!response.ok || !result.ok) {
      throw new Error(result.error || "No fue posible guardar el personaje.");
    }
    return result.avatar;
  };

  populateParts();
  render(currentState);
  triggers.forEach((trigger) => {
    trigger.addEventListener("click", () => {
      render(currentState);
      status.textContent = "";
      dialog.showModal();
    });
  });

  fields.addEventListener("click", (event) => {
    const genderChoice = event.target.closest("[data-avatar-gender-choice]");
    if (genderChoice) {
      render({ ...currentState, gender: genderChoice.dataset.avatarGenderChoice });
      return;
    }
    const choice = event.target.closest("[data-avatar-choice]");
    if (!choice) return;
    render({
      ...currentState,
      selections: { ...currentState.selections, [choice.dataset.avatarSlot]: choice.dataset.avatarPart },
    });
  });
  fields.addEventListener("input", (event) => {
    const input = event.target;
    if (input.matches("[data-avatar-color]")) {
      render({
        ...currentState,
        colors: { ...currentState.colors, [input.dataset.avatarColor]: input.value.toUpperCase() },
      });
    } else if (input.matches("[data-avatar-background]")) {
      render({ ...currentState, background: input.value.toUpperCase() });
    }
  });
  fields.addEventListener("change", (event) => {
    if (event.target.matches("[data-avatar-transparent]")) {
      render({ ...currentState, background: event.target.checked ? "transparent" : "#F6F5F4" });
    }
  });
  dialog.querySelector("[data-avatar-reset]")?.addEventListener("click", () => {
    render(savedState);
    status.textContent = "Se restauró la última versión guardada.";
  });
  dialog.querySelector("[data-avatar-cancel]")?.addEventListener("click", () => {
    render(savedState);
    status.textContent = "";
    dialog.close();
  });
  saveButton.addEventListener("click", async () => {
    saveButton.disabled = true;
    status.textContent = "Guardando tu personaje…";
    try {
      const saved = await saveToServer(currentState);
      savedState = cloneState(saved);
      currentState = cloneState(saved);
      triggers.forEach((trigger) => {
        trigger.dataset.avatarConfig = JSON.stringify(saved);
      });
      render(saved);
      status.textContent = "Tu personaje quedó guardado en tu cuenta.";
      dialog.close();
    } catch (error) {
      status.textContent = error.message || "No fue posible guardar el personaje. Inténtalo de nuevo.";
      console.error("No se pudo guardar el avatar de EDUTURNOS.", error);
    } finally {
      saveButton.disabled = false;
    }
  });
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initialize, { once: true });
} else {
  initialize();
}
