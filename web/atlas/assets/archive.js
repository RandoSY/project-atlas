(() => {
  'use strict';
  const controls = document.querySelector('#search-options');
  const search = document.querySelector('#repo-search');
  const type = document.querySelector('#repo-type');
  const status = document.querySelector('#repo-status');
  const rows = [...document.querySelectorAll('#repo-list li')].map(el => ({
    el, haystack: el.textContent.toLowerCase(), type: el.dataset.kind
  }));
  function filter() {
    const terms = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    let count = 0;
    for (const {el, haystack, type: rowType} of rows) {
      const show = (!type.value || type.value === rowType) && terms.every(t => haystack.includes(t));
      el.hidden = !show;
      if (show) count++;
    }
    status.textContent = count ? `Showing ${count} of ${rows.length} public repositories.` :
      'No repositories match. Try a shorter search or change the repository type.';
  }
  controls.hidden = false;
  search.addEventListener('input', filter);
  type.addEventListener('change', filter);
  filter();
})();
