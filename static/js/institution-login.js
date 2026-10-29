(() => {
  const form = document.querySelector('.login-form');
  if (!form) return;
  const radios = [...form.querySelectorAll('input[name="tipo_acceso"]')];
  const legacy = form.querySelector('[data-jjfh-fields]');
  const hint = form.querySelector('[data-other-institution-hint]');
  const update = () => {
    const isJjfh = form.querySelector('input[name="tipo_acceso"]:checked')?.value !== 'otra';
    if (legacy) legacy.hidden = !isJjfh;
    if (hint) hint.hidden = isJjfh;
    legacy?.querySelectorAll('input,select').forEach((field) => {
      field.disabled = !isJjfh;
      if (!isJjfh) field.value = '';
    });
  };
  radios.forEach((radio) => radio.addEventListener('change', update));
  update();
})();
