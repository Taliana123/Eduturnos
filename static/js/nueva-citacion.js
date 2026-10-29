(() => {
  'use strict';

  const form = document.querySelector('[data-cita-form]');
  if (!form) return;

  const type = form.querySelector('#destinatario-tipo');
  const studentPanel = form.querySelector('[data-student-panel]');
  const personalPanel = form.querySelector('[data-personal-panel]');
  const personal = form.querySelector('#destinatario-personal');
  const search = form.querySelector('#buscar-documento-estudiante');
  const searchButton = form.querySelector('#buscar-estudiante-boton');
  const studentId = form.querySelector('#id-estudiante');
  const studentCard = form.querySelector('#datos-estudiante');
  const guardian = form.querySelector('#acudiente-select');
  const status = form.querySelector('#estado-busqueda-estudiante');
  const personalId = form.querySelector('#destinatario-personal');
  const personalSearch = form.querySelector('#buscar-documento-personal');
  const personalStatus = form.querySelector('#estado-busqueda-personal');
  const personalCard = form.querySelector('#datos-destinatario-personal');
  const studentReasonField = form.querySelector('[data-student-reason-field]');
  const personalReasonField = form.querySelector('[data-personal-reason-field]');
  const studentReason = form.querySelector('#motivo-estudiante');
  const reasonId = form.querySelector('#id-motivo');
  const personalReason = form.querySelector('#motivo-otro');
  let requestSerial = 0;
  let personalRequestSerial = 0;
  let personalTimer = 0;

  function clearStudent(message) {
    studentId.value = '';
    studentCard.hidden = true;
    guardian.replaceChildren(new Option('Primero busca al estudiante por documento', ''));
    guardian.disabled = true;
    guardian.required = false;
    status.textContent = message;
  }

  async function searchStudent() {
    const documentNumber = search.value.trim();
    const serial = ++requestSerial;
    if (!documentNumber) {
      clearStudent('Ingresa el documento y pulsa Buscar.');
      search.focus();
      return;
    }

    status.textContent = 'Buscando estudiante…';
    searchButton.disabled = true;
    try {
      const url = new URL(form.dataset.studentLookupUrl, window.location.origin);
      url.searchParams.set('documento', documentNumber);
      const response = await fetch(url, {
        headers: { Accept: 'application/json' },
        credentials: 'same-origin',
      });
      const data = await response.json();
      if (serial !== requestSerial) return;
      if (!response.ok || !data.ok || !data.estudiante) {
        clearStudent(data.error || 'No se encontró un estudiante activo con ese documento.');
        return;
      }

      studentId.value = data.estudiante.id_estudiante;
      form.querySelector('#nombre-estudiante').textContent =
        `${data.estudiante.nombre} · Documento ${data.estudiante.documento}`;
      form.querySelector('#contexto-estudiante').textContent =
        [data.estudiante.grado, data.estudiante.jornada].filter(Boolean).join(' · ');
      studentCard.hidden = false;
      guardian.replaceChildren();
      const acudientes = data.acudientes || [];
      acudientes.forEach((person) => {
        const option = new Option(
          `${person.nombre}${person.principal ? ' · Acudiente principal' : ''}`,
          person.id_acudiente,
        );
        guardian.add(option);
      });
      const principalId = data.acudiente_principal_id
        || acudientes.find((person) => person.principal)?.id_acudiente
        || acudientes[0]?.id_acudiente;
      if (principalId) guardian.value = String(principalId);
      else guardian.replaceChildren(new Option('No tiene acudiente relacionado', ''));
      guardian.disabled = acudientes.length === 0;
      guardian.required = !guardian.disabled;
      status.textContent = guardian.disabled
        ? 'El estudiante no tiene acudiente relacionado. Pide a coordinación que registre el vínculo antes de crear la citación.'
        : 'Estudiante y acudiente principal cargados automáticamente.';
    } catch (_) {
      if (serial === requestSerial) {
        clearStudent('No se pudo consultar. Revisa la conexión e inténtalo otra vez.');
      }
    } finally {
      if (serial === requestSerial) searchButton.disabled = false;
    }
  }

  function clearPersonal(message) {
    personalId.value = '';
    personalCard.hidden = true;
    personalStatus.textContent = message;
  }

  async function resolvePersonalRecipient() {
    const documentNumber = personalSearch.value.trim();
    const serial = ++personalRequestSerial;
    if (!documentNumber) {
      clearPersonal('Escribe el documento para seleccionar automáticamente el destinatario.');
      return;
    }

    personalStatus.textContent = 'Buscando destinatario…';
    try {
      const url = new URL(form.dataset.personalLookupUrl, window.location.origin);
      url.searchParams.set('documento', documentNumber);
      url.searchParams.set('tipo', type.value);
      const response = await fetch(url, {
        headers: { Accept: 'application/json' },
        credentials: 'same-origin',
      });
      const data = await response.json();
      if (serial !== personalRequestSerial) return;
      if (!response.ok || !data.ok || !data.destinatario) {
        clearPersonal(data.error || 'No se encontró una cuenta activa con ese documento y rol.');
        return;
      }

      personalId.value = data.destinatario.id_usuario;
      personalSearch.setCustomValidity('');
      const displayRole = type.value === 'Administrador / Coordinador' ? 'Coordinador' : type.value === 'Acudiente' ? 'Padre / acudiente' : type.value;
      form.querySelector('[data-personal-role-label]').textContent = displayRole;
      form.querySelector('#nombre-destinatario-personal').textContent =
        `${data.destinatario.nombres} ${data.destinatario.apellidos}`;
      form.querySelector('#documento-destinatario-personal').textContent =
        `Documento ${data.destinatario.documento}`;
      personalCard.hidden = false;
      personalStatus.textContent = `${displayRole} seleccionado automáticamente.`;
    } catch (_) {
      if (serial === personalRequestSerial) {
        clearPersonal('No se pudo consultar. Revisa la conexión e inténtalo otra vez.');
      }
    }
  }

  function applyType() {
    const isStudent = type.value === 'Estudiante';
    const setPanelVisible = (panel, visible) => {
      panel.hidden = !visible;
      panel.setAttribute('aria-hidden', String(!visible));
      if (visible) panel.style.removeProperty('display');
      else panel.style.setProperty('display', 'none', 'important');
    };
    setPanelVisible(studentPanel, isStudent);
    setPanelVisible(personalPanel, !isStudent);
    studentReasonField.hidden = !isStudent;
    studentReason.disabled = !isStudent;
    studentReason.required = isStudent;
    personalReasonField.hidden = isStudent;
    personalReason.disabled = isStudent;
    personalReason.required = !isStudent;
    reasonId.value = isStudent ? studentReason.value : form.dataset.otherReasonId;

    search.disabled = !isStudent;
    searchButton.disabled = !isStudent;
    studentId.disabled = !isStudent;
    studentId.required = isStudent;
    guardian.disabled = !isStudent || guardian.options.length === 0;
    guardian.required = isStudent && guardian.options.length > 0;
    personalSearch.disabled = isStudent;
    personalSearch.required = !isStudent;
    personalSearch.setCustomValidity('');

    if (isStudent) {
      window.clearTimeout(personalTimer);
      personalRequestSerial += 1;
      personalSearch.value = '';
      clearPersonal('Selecciona Estudiante en el tipo de destinatario.');
    } else {
      requestSerial += 1;
      search.value = '';
      clearStudent('Elige el destinatario institucional correspondiente a este tipo.');
      personalSearch.value = '';
      const roleLabel = type.value === 'Docente'
        ? 'docente'
        : type.value === 'Administrador / Coordinador'
          ? 'coordinador'
          : type.value === 'Acudiente'
            ? 'padre o acudiente'
            : 'rector';
      form.querySelector('#personal-mode-title').textContent = type.value === 'Acudiente'
        ? 'Citación para padre o acudiente'
        : 'Citación para personal institucional';
      personalSearch.placeholder = `Documento del ${roleLabel}`;
      form.querySelector('[data-personal-search-label]').textContent =
        `Buscar ${roleLabel} por número de documento`;
      personalRequestSerial += 1;
      clearPersonal('Escribe el documento para seleccionar automáticamente el destinatario.');
    }
  }

  searchButton.addEventListener('click', searchStudent);
  search.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      searchStudent();
    }
  });
  search.addEventListener('input', () => {
    requestSerial += 1;
    clearStudent('Documento modificado. Pulsa Buscar para cargar los datos.');
  });
  type.addEventListener('change', applyType);
  studentReason.addEventListener('change', () => { reasonId.value = studentReason.value; });
  personalSearch.addEventListener('input', () => {
    personalRequestSerial += 1;
    personalSearch.setCustomValidity('');
    clearPersonal(personalSearch.value.trim() ? 'Consultando el documento…' : 'Escribe el documento para seleccionar automáticamente el destinatario.');
    window.clearTimeout(personalTimer);
    if (personalSearch.value.trim().length >= 4) {
      personalTimer = window.setTimeout(resolvePersonalRecipient, 350);
    }
  });
  personalSearch.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      window.clearTimeout(personalTimer);
      resolvePersonalRecipient();
    }
  });
  form.addEventListener('submit', (event) => {
    if (type.value !== 'Estudiante' && !personalId.value) {
      event.preventDefault();
      personalSearch.setCustomValidity('Ingresa un documento válido y espera a que se seleccione el destinatario.');
      personalSearch.reportValidity();
    }
  });
  form.addEventListener('reset', () => {
    window.setTimeout(() => {
      search.value = '';
      clearStudent('Ingresa el documento y pulsa Buscar.');
      personalSearch.value = '';
      clearPersonal('Escribe el documento para seleccionar automáticamente el destinatario.');
      applyType();
    }, 0);
  });

  applyType();
})();
