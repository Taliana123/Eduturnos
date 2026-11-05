(() => {
  'use strict';

  const table = document.querySelector('.solicitudes-table');
  if (!table) return;

  function setToggleState(row, expanded) {
    row.classList.toggle('is-expanded', expanded);
    const button = row.querySelector('[data-request-toggle]');
    if (!button) return;
    const label = button.closest('td').querySelector('strong').textContent.trim();
    button.setAttribute('aria-expanded', String(expanded));
    button.setAttribute('aria-label', `${expanded ? 'Cerrar' : 'Abrir'} ${label}`);
    button.innerHTML = expanded
      ? 'Cerrar <span aria-hidden="true">⌃</span>'
      : 'Abrir <span aria-hidden="true">⌄</span>';
  }

  table.addEventListener('click', (event) => {
    const button = event.target.closest('[data-request-toggle]');
    if (!button) return;

    const row = button.closest('tr');
    if (!row) return;

    const expanded = !row.classList.contains('is-expanded');
    if (expanded) {
      table.querySelectorAll('tbody tr.is-expanded').forEach((openRow) => setToggleState(openRow, false));
    }
    setToggleState(row, expanded);
  });
})();
