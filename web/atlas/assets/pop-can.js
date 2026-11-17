(() => {
  'use strict';
  const $ = s => document.querySelector(s);
  if (!$('[data-pop-can-model]')) return;
  const field = s => $(s), number = s => field(s).valueAsNumber;
  const note = $('#pc-model-note');
  function render() {
    const ids = ['#pc-water', '#pc-delta', '#pc-fuel', '#pc-time'];
    const [water, delta, fuel, t] = ids.map(number);
    if (ids.some(s => !Number.isFinite(number(s)) || !field(s).validity.valid)) {
      for (const s of ['#pc-heat', '#pc-power', '#pc-per-gram', '#pc-ymax', '#pc-yavg', '#pc-tmax']) $(s).textContent = '—';
      $('#pc-area').setAttribute('d', '');
      $('#pc-trace').setAttribute('d', '');
      note.textContent = 'Enter a value within each field’s allowed range.';
      return;
    }
    const j = water * 4.184 * delta, watts = j / t;
    $('#pc-heat').value = `${(j / 1000).toFixed(2)} kJ`;
    $('#pc-power').value = `${watts.toFixed(2)} W`;
    $('#pc-per-gram').value = fuel > 0 ? `${(j / 1000 / fuel).toFixed(2)} kJ/g` : '—';
    const ymax = watts > 0 ? watts * 2 : 1;
    $('#pc-ymax').textContent = ymax.toFixed(1);
    $('#pc-yavg').textContent = (ymax / 2).toFixed(1);
    $('#pc-tmax').textContent = `${t} s`;
    const front = $('#pc-profile').value === 'front';
    const y = power => 163 - 136 * power / ymax;
    const ya = y(watts * (front ? 1.6 : 1)), yb = y(watts * (front ? .4 : 1));
    $('#pc-trace').setAttribute('d', `M78 ${ya} L475 ${yb}`);
    $('#pc-area').setAttribute('d', `M78 163 L78 ${ya} L475 ${yb} L475 163 Z`);
    note.textContent = fuel > 0
      ? 'The shaded area is the net heat added to the water. The model does not estimate the candle’s total power.'
      : 'Water heat and rate are still calculable. Heat per gram is undefined when no candle mass loss is entered.';
  }
  document.querySelector('[data-pop-can-model]').addEventListener('input', render);
  document.querySelector('[data-pop-can-model]').addEventListener('change', render);
  render();
})();
