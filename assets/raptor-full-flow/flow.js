/* GIF progressive-enhancement: il poster resta leggibile anche senza JavaScript. */
(() => {
  'use strict';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('[data-raptor-flow]').forEach(figure => {
    const image = figure.querySelector('img[data-gif]');
    const button = figure.querySelector('[data-flow-toggle]');
    const status = figure.querySelector('[data-flow-status]');
    const controls = figure.querySelector('.raptor-flow-controls');
    if (!image || !button || !status || !controls) return;
    const poster = image.getAttribute('src');
    const gif = image.dataset.gif;
    let visible = false, playing = false, intent = null, failed = false;
    function setPlaying(next) {
      if (next !== playing) {
        playing = next;
        image.src = next ? gif : poster;
      }
      figure.dataset.playing = String(playing);
      button.textContent = playing ? 'Mostra schema statico' : 'Avvia animazione';
      status.textContent = playing
        ? 'Flussi animati. Velocità illustrative.'
        : failed ? 'Animazione non caricata: schema statico disponibile.'
        : reduced.matches && intent !== true ? 'Movimento ridotto: schema statico.'
        : 'Schema statico. Sul telefono puoi scorrere la tavola.';
    }
    function update() {
      setPlaying(!failed && visible && !document.hidden &&
        (intent === true || (intent === null && !reduced.matches)));
    }
    button.hidden = false;
    button.addEventListener('click', () => { intent = !playing; update(); });
    image.addEventListener('error', () => {
      if (!playing) return;
      failed = true;
      button.disabled = true;
      update();
    });
    const zoom = document.createElement('button');
    zoom.type = 'button'; zoom.textContent = 'Ingrandisci';
    zoom.setAttribute('aria-pressed', 'false');
    zoom.setAttribute('aria-label', 'Ingrandisci lo schema nella pagina');
    zoom.addEventListener('click', () => {
      const enlarged = figure.classList.toggle('is-zoomed');
      zoom.setAttribute('aria-pressed', String(enlarged));
      zoom.textContent = enlarged ? 'Adatta alla pagina' : 'Ingrandisci';
    });
    button.after(zoom);
    // Una GIF non si ferma sul singolo fotogramma: il comando mostra il poster.
    // Fuori schermo non continua a decodificare i fotogrammi.
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => {
        visible = entries[0].isIntersecting; update();
      }, {threshold: 0});
      observer.observe(figure);
    } else { visible = true; }
    document.addEventListener('visibilitychange', update);
    reduced.addEventListener('change', () => { intent = null; update(); });
    update();
  });
})();
