(() => {
  const form = document.querySelector('.login-form');
  if (!form) return;
  const choice = form.querySelector('[data-institution-choice]');
  const institutionWrap = form.querySelector('[data-other-institutions]');
  const institutionList = form.querySelector('[data-institution-list]');
  const legacy = form.querySelector('[data-jjfh-fields]');
  const hint = form.querySelector('[data-other-institution-hint]');
  const identifier = form.querySelector('[name="identificador"]');
  const staffCodeField = legacy?.querySelector('[data-staff-code-field]');
  const staffCodeInput = staffCodeField?.querySelector('input[name="codigo_institucional"]');
  const update = () => {
    const isJjfh = choice?.value !== 'otra';
    const isInstitutionalStaffEmail = /@jjfh\.edu\.co$/i.test(identifier?.value.trim() || '');
    if (institutionWrap) institutionWrap.hidden = isJjfh;
    if (institutionList) {
      institutionList.disabled = isJjfh;
      institutionList.required = !isJjfh;
      if (isJjfh) institutionList.value = '';
    }
    if (legacy) legacy.hidden = !isJjfh;
    if (hint) hint.hidden = isJjfh;
    legacy?.querySelectorAll('input,select').forEach((field) => {
      field.disabled = !isJjfh || (field === staffCodeInput && !isInstitutionalStaffEmail);
      if (!isJjfh) field.value = '';
    });
    if (staffCodeField) staffCodeField.hidden = !isJjfh || !isInstitutionalStaffEmail;
    if (staffCodeInput && (!isJjfh || !isInstitutionalStaffEmail)) {
      staffCodeInput.value = '';
    }
  };
  choice?.addEventListener('change', update);
  identifier?.addEventListener('input', update);
  update();
})();
