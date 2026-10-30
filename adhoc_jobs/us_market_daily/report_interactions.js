(() => {
  const dialog = document.getElementById('chart-dialog');
  const enlarged = document.getElementById('zoom-image');
  let chartTrigger;
  document.querySelectorAll('.chart-button').forEach(button => {
    button.addEventListener('click', () => {
      const image = button.querySelector('img');
      enlarged.src = image.src;
      enlarged.alt = image.alt;
      document.getElementById('chart-title').textContent = image.alt;
      chartTrigger = button;
      dialog.showModal();
    });
  });
  document.getElementById('close-chart').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => { enlarged.removeAttribute('src'); chartTrigger?.focus(); });
  document.getElementById('print-report').addEventListener('click', () => window.print());
  function revealHash() {
    const id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    const target = document.getElementById(id);
    if (!target) return;
    if (target.matches('details')) target.open = true;
    for (let node = target.parentElement; node; node = node.parentElement) {
      if (node.matches('details')) node.open = true;
    }
    target.scrollIntoView({ block: 'start' });
  }
  window.addEventListener('hashchange', revealHash);
  revealHash();
  document.querySelectorAll('#watchlist tbody tr').forEach(row => {
    const change = row.cells[2];
    if (change) change.classList.add(change.textContent.trim().startsWith('-') ? 'negative' : 'positive');
  });
  const links = [...document.querySelectorAll('.navigation a')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.filter(entry => entry.isIntersecting).forEach(entry => {
        links.forEach(link => {
          if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-80px 0px -65% 0px', threshold: 0 });
    links.forEach(link => { const target = document.querySelector(link.hash); if (target) observer.observe(target); });
  }
})();
