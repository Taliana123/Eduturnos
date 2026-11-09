import { createAvatar, createPartPreview, getPartsForSlot } from "@humation/core";
import { humation1 } from "@humation/assets-humation-1";

const slots = [
  ["head", "Pelo y cabeza"],
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
const genderPresets = {
  mujer: { head: "hm1-p-000024", body: "hm1-p-000030", bottom: "hm1-p-000036" },
  hombre: { head: "hm1-p-000003", body: "hm1-p-000028", bottom: "hm1-p-000034" },
  nina: { head: "hm1-p-000016", body: "hm1-p-000025", bottom: "hm1-p-000037" },
  nino: { head: "hm1-p-000007", body: "hm1-p-000032", bottom: "hm1-p-000033" },
};
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
    const categoryList = document.createElement("nav");
    categoryList.className = "avatar-category-list";
    categoryList.dataset.avatarCategoryList = "";
    categoryList.setAttribute("aria-label", "Categorías del personaje");
    const categoryPanels = document.createElement("div");
    categoryPanels.className = "avatar-category-panels";

    const createCategory = (id, title) => {
      const link = document.createElement("button");
      link.type = "button";
      link.className = "avatar-category-link";
      link.dataset.avatarCategory = id;
      link.setAttribute("aria-controls", `avatar-category-${id}`);
      link.textContent = title;
      categoryList.append(link);

      const panel = document.createElement("section");
      panel.className = "avatar-category-panel";
      panel.id = `avatar-category-${id}`;
      panel.dataset.avatarCategoryPanel = id;
      panel.setAttribute("aria-labelledby", `avatar-category-title-${id}`);
      panel.hidden = true;
      const header = document.createElement("div");
      header.className = "avatar-category-header";
      const back = document.createElement("button");
      back.type = "button";
      back.className = "avatar-category-back";
      back.dataset.avatarCategoryBack = "";
      back.setAttribute("aria-label", "Volver a las categorías");
      back.title = "Volver a las categorías";
      back.innerHTML = '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M19 12H5m7 7-7-7 7-7"></path></svg>';
      const heading = document.createElement("h3");
      heading.id = `avatar-category-title-${id}`;
      heading.textContent = title;
      header.append(back, heading);
      panel.append(header);
      const content = document.createElement("div");
      content.className = "avatar-category-content";
      panel.append(content);
      categoryPanels.append(panel);
      return content;
    };

    fields.append(categoryList, categoryPanels);

    const genderContent = createCategory("gender", "Género");
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
    genderHint.textContent = "Al elegir un género se aplica un estilo inicial; después puedes personalizar cada rasgo.";
    genderGroup.append(genderOptions, genderHint);
    genderContent.append(genderGroup);

    for (const [slot, title] of slots) {
      const content = createCategory(slot, title);
      const group = document.createElement("div");
      group.className = "avatar-option-group";
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
      content.append(group);
    }

    const colorsContent = createCategory("colors", "Colores");
    const colorsGroup = document.createElement("div");
    colorsGroup.className = "avatar-option-group avatar-color-group";
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
    colorsContent.append(colorsGroup);
  };

  const showCategory = (category) => {
    const categoryList = fields.querySelector("[data-avatar-category-list]");
    const panels = [...fields.querySelectorAll("[data-avatar-category-panel]")];
    const activePanel = panels.find((panel) => panel.dataset.avatarCategoryPanel === category);
    if (!activePanel) return;
    categoryList.hidden = true;
    panels.forEach((panel) => {
      panel.hidden = panel !== activePanel;
    });
  };

  const showCategoryList = () => {
    fields.querySelector("[data-avatar-category-list]").hidden = false;
    fields.querySelectorAll("[data-avatar-category-panel]").forEach((panel) => {
      panel.hidden = true;
    });
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
      showCategoryList();
      status.textContent = "";
      dialog.showModal();
    });
  });

  fields.addEventListener("click", (event) => {
    const categoryLink = event.target.closest("[data-avatar-category]");
    if (categoryLink) {
      showCategory(categoryLink.dataset.avatarCategory);
      return;
    }
    if (event.target.closest("[data-avatar-category-back]")) {
      showCategoryList();
      return;
    }
    const genderChoice = event.target.closest("[data-avatar-gender-choice]");
    if (genderChoice) {
      const gender = genderChoice.dataset.avatarGenderChoice;
      render({
        ...currentState,
        gender,
        selections: { ...currentState.selections, ...genderPresets[gender] },
      });
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
  const discardChanges = () => {
    render(savedState);
    status.textContent = "";
  };
  dialog.querySelectorAll("[data-avatar-cancel]").forEach((cancelButton) => {
    cancelButton.addEventListener("click", () => {
      discardChanges();
      dialog.close();
    });
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
    if (event.target === dialog) {
      discardChanges();
      dialog.close();
    }
  });
  dialog.addEventListener("cancel", () => {
    discardChanges();
  });
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initialize, { once: true });
} else {
  initialize();
}
