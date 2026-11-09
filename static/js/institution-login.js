(() => {
  const form = document.querySelector('.login-form');
  if (!form) return;
  const choice = form.querySelector('[data-institution-choice]');
  const institutionWrap = form.querySelector('[data-other-institutions]');
  const institutionList = form.querySelector('[data-institution-list]');
  const legacy = form.querySelector('[data-jjfh-fields]');
  const hint = form.querySelector('[data-other-institution-hint]');
  const update = () => {
    const isJjfh = choice?.value !== 'otra';
    if (institutionWrap) institutionWrap.hidden = isJjfh;
    if (institutionList) {
      institutionList.disabled = isJjfh;
      institutionList.required = !isJjfh;
      if (isJjfh) institutionList.value = '';
    }
    if (legacy) legacy.hidden = !isJjfh;
    if (hint) hint.hidden = isJjfh;
    legacy?.querySelectorAll('input,select').forEach((field) => {
      field.disabled = !isJjfh;
      if (!isJjfh) field.value = '';
    });
  };
  choice?.addEventListener('change', update);
  update();
})();
