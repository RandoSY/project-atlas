(() => {
  'use strict';
  const $ = s => document.querySelector(s);
  if (!$('[data-singing-lab]')) return;
  const length = $('#sr-length'), damping = $('#sr-damping');
  const frequency = () => 8 * (20 / Number(length.value)) ** 2;
  const decay = () => Number(damping.value);
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let frame = 0, audio, activeGain, activeOscillator;

  function ruler(dy = 0) {
    const x = 95 + 12.5 * Number(length.value);
    $('#sr-beam').setAttribute('d', `M95 69 Q${95 + (x - 95) * .54} 69 ${x} ${69 + dy}`);
    $('#sr-tip').setAttribute('cx', x);
    $('#sr-tip').setAttribute('cy', 69 + dy);
    $('#sr-tip-label').setAttribute('x', Math.min(440, x - 23));
  }
  function clearAnimation() {
    cancelAnimationFrame(frame);
    frame = 0;
    ruler();
  }
  function render() {
    clearAnimation();
    const f = frequency();
    $('#sr-lval').value = `${length.value} cm`;
    $('#sr-dval').value = `${decay().toFixed(1)} s⁻¹`;
    $('#sr-hz').value = `${f.toFixed(2)} Hz`;
    const trace = Array.from({length: 461}, (_, i) => {
      const t = 2 * i / 460;
      const y = 62 - 38 * Math.exp(-decay() * t) * Math.cos(2 * Math.PI * f * t);
      return `${i ? 'L' : 'M'}${(35 + 445 * i / 460).toFixed(1)} ${y.toFixed(2)}`;
    });
    $('#sr-trace').setAttribute('d', trace.join(' '));
  }
  async function tone() {
    if (!$('#sr-sound').checked) return;
    const Context = window.AudioContext || window.webkitAudioContext;
    if (!Context) {
      $('#sr-caption').textContent = 'Audio is unavailable in this browser. The plotted model is still available.';
      return;
    }
    try {
      audio ||= new Context();
      await audio.resume();
      if (activeGain && activeOscillator) {
        activeGain.gain.cancelScheduledValues(audio.currentTime);
        activeGain.gain.setTargetAtTime(0, audio.currentTime, .012);
        try { activeOscillator.stop(audio.currentTime + .045); } catch {}
      }
      const now = audio.currentTime, osc = audio.createOscillator(), gain = audio.createGain();
      osc.frequency.value = 32 * frequency();
      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(.09, now + .018);
      gain.gain.setTargetAtTime(0, now + .018, .48 / decay());
      osc.connect(gain).connect(audio.destination);
      osc.start(now); osc.stop(now + 2.8);
      activeGain = gain; activeOscillator = osc;
    } catch {
      $('#sr-caption').textContent = 'Audio could not start. The plotted model is still available.';
    }
  }
  $('#sr-pluck').addEventListener('click', () => {
    clearAnimation();
    if (!reduced.matches) {
      let start;
      const k = decay(), f = frequency();
      const step = now => {
        start ??= now;
        const t = (now - start) / 1000;
        if (t >= 2.8) return clearAnimation();
        ruler(24 * Math.exp(-k * t) * Math.cos(2 * Math.PI * f * t));
        frame = requestAnimationFrame(step);
      };
      frame = requestAnimationFrame(step);
    }
    void tone();
  });
  length.addEventListener('input', render);
  damping.addEventListener('input', render);
  render();
})();
