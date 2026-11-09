(() => {
  'use strict';

  const form = document.querySelector('[data-cita-form]');
  if (!form) return;

  const type = form.querySelector('#destinatario-tipo');
  const studentPanel = form.querySelector('[data-student-panel]');
  const personalPanel = form.querySelector('[data-personal-panel]');
  const search = form.querySelector('#buscar-documento-estudiante');
  const searchButton = form.querySelector('#buscar-estudiante-boton');
  const studentSuggestions = form.querySelector('#coincidencias-estudiante');
  const studentId = form.querySelector('#id-estudiante');
  const studentCard = form.querySelector('#datos-estudiante');
  const guardian = form.querySelector('#acudiente-select');
  const status = form.querySelector('#estado-busqueda-estudiante');
  const personalId = form.querySelector('#destinatario-personal');
  const personalSearch = form.querySelector('#buscar-documento-personal');
  const personalSuggestions = form.querySelector('#coincidencias-personal');
  const personalStatus = form.querySelector('#estado-busqueda-personal');
  const personalCard = form.querySelector('#datos-destinatario-personal');
  const studentReasonField = form.querySelector('[data-student-reason-field]');
  const personalReasonField = form.querySelector('[data-personal-reason-field]');
  const studentReason = form.querySelector('#motivo-estudiante');
  const reasonId = form.querySelector('#id-motivo');
  const personalReason = form.querySelector('#motivo-personal');
  const appointmentTime = form.querySelector('#hora-cita');
  let requestSerial = 0;
  let studentSuggestionSerial = 0;
  let personalRequestSerial = 0;
  let personalSuggestionSerial = 0;
  let personalTimer = 0;
  let studentTimer = 0;

  function clearStudent(message) {
    studentId.value = '';
    studentCard.hidden = true;
    studentSuggestions.replaceChildren();
    studentSuggestions.hidden = true;
    guardian.replaceChildren(new Option('Primero busca al estudiante por documento', ''));
    guardian.disabled = true;
    guardian.required = false;
    status.textContent = message;
  }

  function filterTimesByJourney(journey) {
    const normalizedJourney = String(journey || '').trim().toLocaleLowerCase('es');
    const restrictedShift = normalizedJourney === 'mañana' || normalizedJourney === 'tarde';
    const selectedTime = appointmentTime.value;

    Array.from(appointmentTime.querySelectorAll('optgroup')).forEach((group) => {
      const shift = group.label.trim().toLocaleLowerCase('es');
      group.hidden = restrictedShift && shift !== normalizedJourney;
    });

    if (selectedTime) {
      const selectedOption = Array.from(appointmentTime.options)
        .find((option) => option.value === selectedTime);
      if (selectedOption?.parentElement?.hidden) appointmentTime.value = '';
    }
  }

  function renderSuggestions(container, matches, chooseMatch, getDetails) {
    container.replaceChildren();
    matches.forEach((match) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'citation-suggestion';
      button.setAttribute('role', 'option');
      const name = document.createElement('span');
      name.textContent = match.nombre
        || `${match.nombres || ''} ${match.apellidos || ''}`.trim();
      const details = document.createElement('small');
      details.textContent = getDetails(match);
      button.append(name, details);
      button.addEventListener('click', () => chooseMatch(match));
      container.append(button);
    });
    container.hidden = matches.length === 0;
  }

  async function suggestStudents() {
    const documentNumber = search.value.trim();
    const serial = ++studentSuggestionSerial;
    if (documentNumber.length < 2) {
      studentSuggestions.replaceChildren();
      studentSuggestions.hidden = true;
      return;
    }

    try {
      const url = new URL(form.dataset.studentLookupUrl, window.location.origin);
      url.searchParams.set('documento', documentNumber);
      url.searchParams.set('coincidencias', '1');
      const response = await fetch(url, {
        headers: { Accept: 'application/json' },
        credentials: 'same-origin',
      });
      const data = await response.json();
      if (serial !== studentSuggestionSerial || search.value.trim() !== documentNumber) return;
      const matches = response.ok && data.ok ? (data.estudiantes || []) : [];
      renderSuggestions(studentSuggestions, matches, (student) => {
        window.clearTimeout(studentTimer);
        search.value = student.documento;
        studentSuggestions.replaceChildren();
        studentSuggestions.hidden = true;
        searchStudent();
      }, (student) => [
        `Documento ${student.documento}`,
        student.grado && `Grado ${student.grado}`,
        student.jornada,
      ].filter(Boolean).join(' · '));
      status.textContent = matches.length
        ? 'Selecciona al estudiante que coincide con el documento.'
        : 'No hay estudiantes activos que coincidan con ese documento.';
    } catch (_) {
      if (serial === studentSuggestionSerial) {
        studentSuggestions.replaceChildren();
        studentSuggestions.hidden = true;
        status.textContent = 'No se pudieron cargar las coincidencias. Puedes pulsar Buscar.';
      }
    }
  }

  async function searchStudent() {
    const documentNumber = search.value.trim();
    const serial = ++requestSerial;
    studentSuggestionSerial += 1;
    window.clearTimeout(studentTimer);
    studentSuggestions.replaceChildren();
    studentSuggestions.hidden = true;
    if (!documentNumber) {
      clearStudent('Escribe el documento para ver coincidencias.');
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
      filterTimesByJourney(data.estudiante.jornada);
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
    personalSuggestions.replaceChildren();
    personalSuggestions.hidden = true;
    personalStatus.textContent = message;
  }

  async function suggestPersonalRecipients() {
    const documentNumber = personalSearch.value.trim();
    const serial = ++personalSuggestionSerial;
    if (documentNumber.length < 2) {
      personalSuggestions.replaceChildren();
      personalSuggestions.hidden = true;
      return;
    }

    try {
      const url = new URL(form.dataset.personalLookupUrl, window.location.origin);
      url.searchParams.set('documento', documentNumber);
      url.searchParams.set('tipo', type.value);
      url.searchParams.set('coincidencias', '1');
      const response = await fetch(url, {
        headers: { Accept: 'application/json' },
        credentials: 'same-origin',
      });
      const data = await response.json();
      if (serial !== personalSuggestionSerial || personalSearch.value.trim() !== documentNumber) return;
      const matches = response.ok && data.ok ? (data.destinatarios || []) : [];
      renderSuggestions(personalSuggestions, matches, (recipient) => {
        window.clearTimeout(personalTimer);
        personalSearch.value = recipient.documento;
        personalSuggestions.replaceChildren();
        personalSuggestions.hidden = true;
        resolvePersonalRecipient();
      }, (recipient) => `Documento ${recipient.documento} · ${recipient.rol_nombre}`);
      personalStatus.textContent = matches.length
        ? 'Selecciona el destinatario que coincide con el documento.'
        : 'No hay cuentas activas que coincidan con ese documento.';
    } catch (_) {
      if (serial === personalSuggestionSerial) {
        personalSuggestions.replaceChildren();
        personalSuggestions.hidden = true;
        personalStatus.textContent = 'No se pudieron cargar las coincidencias.';
      }
    }
  }

  async function resolvePersonalRecipient() {
    const documentNumber = personalSearch.value.trim();
    const serial = ++personalRequestSerial;
    personalSuggestionSerial += 1;
    window.clearTimeout(personalTimer);
    personalSuggestions.replaceChildren();
    personalSuggestions.hidden = true;
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
    reasonId.value = isStudent ? studentReason.value : (form.dataset.otherReasonId || '');
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
      window.clearTimeout(studentTimer);
      personalRequestSerial += 1;
      personalSuggestionSerial += 1;
      studentSuggestionSerial += 1;
      personalSearch.value = '';
      clearPersonal('Selecciona Estudiante en el tipo de destinatario.');
      filterTimesByJourney('');
    } else {
      requestSerial += 1;
      studentSuggestionSerial += 1;
      window.clearTimeout(studentTimer);
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
    studentSuggestionSerial += 1;
    window.clearTimeout(studentTimer);
    search.setCustomValidity('');
    filterTimesByJourney('');
    clearStudent('Escribe el documento para ver coincidencias.');
    if (search.value.trim().length >= 2) {
      studentTimer = window.setTimeout(suggestStudents, 200);
    }
  });
  type.addEventListener('change', applyType);
  type.addEventListener('input', applyType);
  studentReason.addEventListener('change', () => {
    reasonId.value = studentReason.value;
    studentReason.setCustomValidity('');
  });
  personalSearch.addEventListener('input', () => {
    personalRequestSerial += 1;
    personalSuggestionSerial += 1;
    personalSearch.setCustomValidity('');
    clearPersonal(personalSearch.value.trim()
      ? 'Buscando coincidencias…'
      : 'Escribe el documento para ver coincidencias.');
    window.clearTimeout(personalTimer);
    if (personalSearch.value.trim().length >= 2) {
      personalTimer = window.setTimeout(suggestPersonalRecipients, 200);
    }
  });
  personalReason.addEventListener('input', () => {
    personalReason.setCustomValidity('');
  });
  personalSearch.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      window.clearTimeout(personalTimer);
      if (!personalSuggestions.hidden) {
        personalSuggestions.querySelector('button')?.focus();
      } else {
        resolvePersonalRecipient();
      }
    }
  });
  form.addEventListener('submit', (event) => {
    if (type.value === 'Estudiante' && !studentId.value) {
      event.preventDefault();
      search.setCustomValidity('Busca y selecciona al estudiante por número de documento.');
      search.reportValidity();
      return;
    }
    if (type.value !== 'Estudiante' && !personalId.value) {
      event.preventDefault();
      personalSearch.setCustomValidity('Ingresa un documento válido y espera a que se seleccione el destinatario.');
      personalSearch.reportValidity();
      return;
    }
    if (type.value === 'Estudiante' && !studentReason.value) {
      event.preventDefault();
      studentReason.setCustomValidity('Selecciona el motivo de la citación.');
      studentReason.reportValidity();
      return;
    }
    if (type.value !== 'Estudiante' && !personalReason.value.trim()) {
      event.preventDefault();
      personalReason.setCustomValidity('Escribe el motivo de la citación.');
      personalReason.reportValidity();
    }
  });
  form.addEventListener('reset', () => {
    window.setTimeout(() => {
      search.value = '';
      clearStudent('Escribe el documento para ver coincidencias.');
      personalSearch.value = '';
      clearPersonal('Escribe el documento para seleccionar automáticamente el destinatario.');
      applyType();
      studentReason.value = '';
      reasonId.value = '';
      personalReason.value = '';
    }, 0);
  });

  applyType();
  // Reapply the correct recipient panel when mobile browsers restore this
  // form from the back/forward cache after a validation redirect.
  window.addEventListener('pageshow', applyType);
})();
