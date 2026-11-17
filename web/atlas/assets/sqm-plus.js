(() => {
  'use strict';
  const $ = s => document.querySelector(s);
  if (!$('[data-sqm-widget]')) return;
  const time = $('#sq-time'), steps = $('#sq-steps');
  function render() {
    const t = Number(time.value), n = Number(steps.value), diff = n - 20;
    $('#sq-time-value').value = `${t.toFixed(1)} s`;
    $('#sq-step-value').value = n;
    $('#sq-speed').value = `${(11 / t).toFixed(2)} m/s`;
    $('#sq-cadence').value = `${(60 * n / t).toFixed(1)} per min`;
    $('#sq-length').value = `${(11 / n).toFixed(2)} m`;
    $('#sq-error').value = diff > 0 ? `+${diff}` : String(diff);
  }
  time.addEventListener('input', render);
  steps.addEventListener('input', render);
  render();
})();
