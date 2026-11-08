/* Istanti assoluti: nessuna dipendenza dal fuso orario del browser.
   A zero non viene mai dichiarato automaticamente un decollo. */
(()=>{
  'use strict';
  const cards=[...document.querySelectorAll('[data-launch-window]')];
  if(!cards.length)return;
  const pad=n=>String(n).padStart(2,'0');
  function update(card,now){
    const start=Date.parse(card.dataset.start),end=Date.parse(card.dataset.end);
    const valid=Number.isFinite(start)&&Number.isFinite(end)&&end>start;
    const phase=!valid?'unknown':now<start?'pending':now<end?'open':'ended';
    if(card.dataset.windowPhase!==phase){
      card.dataset.windowPhase=phase;
      card.querySelector('[data-window-state]').textContent={
        pending:'Conto alla rovescia all’apertura',
        open:'Orario di apertura raggiunto · finestra prevista in corso',
        ended:'Finestra prevista terminata · verifica gli aggiornamenti',
        unknown:'Orario non disponibile · consulta gli aggiornamenti'
      }[phase];
    }
    const total=phase==='pending'?Math.max(0,Math.ceil((start-now)/1000)):0;
    const parts={days:pad(Math.floor(total/86400)),hours:pad(Math.floor(total%86400/3600)),minutes:pad(Math.floor(total%3600/60)),seconds:pad(total%60)};
    for(const [name,value]of Object.entries(parts)){
      const cell=card.querySelector(`[data-window-part="${name}"]`);
      const next=valid?value:'—';
      if(cell&&cell.textContent!==next)cell.textContent=next;
    }
  }
  const tick=()=>{const now=Date.now();cards.forEach(card=>update(card,now));};
  tick();
  setInterval(tick,1000);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)tick();});
  window.addEventListener('pageshow',tick);
})();
