/* Animazione deterministica: nessuna rete, nessun dato o valore Raptor stimato. */
(() => {
  const svg=document.querySelector('main svg');
  const NS='http://www.w3.org/2000/svg';
  const tracerLayer=svg.querySelector('#flow-tracers');
  const flows=window.flowConfig.flows.filter(f=>!f.id.includes('pump-inside')&&!f.id.includes('turbine-inside')).map(f=>{
    const route=svg.querySelector(`#${f.id}`);
    const length=route.getTotalLength();
    const count=Math.max(1,Math.round(length/f.spacing));
    const little=f.width<10;
    const r=little?3.3:f.kind==='liquid'?6:7;
    const tracers=[];
    for(let i=0;i<count;i++) {
      const g=document.createElementNS(NS,'g');
      const p=document.createElementNS(NS,'path');
      p.setAttribute('d',`M${-r} ${-r*.72}L${r*.12} 0L${-r} ${r*.72}M${-r*.1} ${-r*.72}L${r*1.03} 0L${-r*.1} ${r*.72}`);
      p.setAttribute('fill','none');p.setAttribute('stroke',f.color);
      p.setAttribute('stroke-width',little?'1.6':'2.6');
      p.setAttribute('stroke-linecap','round');p.setAttribute('stroke-linejoin','round');
      const tip=document.createElementNS(NS,'circle');
      tip.setAttribute('cx',r*.95);tip.setAttribute('cy','0');
      tip.setAttribute('r',little?'1':'1.8');tip.setAttribute('fill','#fff4d9');
      g.append(p,tip);tracerLayer.appendChild(g);tracers.push(g);
    }
    const speed=f.kind==='exhaust'?100:f.kind==='gas'?80:60;
    const advances=Math.max(1,Math.round(speed*6/(length/count)));
    return {...f,route,length,count,tracers,advances};
  });
  const rotors=[...svg.querySelectorAll('[data-rotor]')];
  function setFrame(t) {
    const phase=((t%6)+6)%6/6;
    for(const f of flows) {
      // Un numero intero di percorsi per ciclo evita salti quando il ciclo ricomincia.
      for(let i=0;i<f.count;i++) {
        const progress=(i/f.count+phase*f.advances/f.count)%1;
        const d=progress*f.length;
        const p=f.route.getPointAtLength(d);
        const p0=f.route.getPointAtLength(Math.max(0,d-.4));
        const p1=f.route.getPointAtLength(Math.min(f.length,d+.4));
        const angle=Math.atan2(p1.y-p0.y,p1.x-p0.x)*180/Math.PI;
        const opacity=Math.min(1,d/10,(f.length-d)/10);
        f.tracers[i].setAttribute('transform',`translate(${p.x.toFixed(3)} ${p.y.toFixed(3)}) rotate(${angle.toFixed(3)})`);
        f.tracers[i].setAttribute('opacity',Math.max(0,opacity).toFixed(3));
      }
    }
    for(const r of rotors) {
      // Una sola rotazione lenta per ciclo: evita l'aliasing delle palette ripetute.
      const angle=phase*360;
      r.setAttribute('transform',`translate(${r.dataset.cx} ${r.dataset.cy}) rotate(${angle})`);
    }
    svg.setAttribute('data-time',t.toFixed(5));
  }
  window.setDiagramTime=setFrame;
  window.diagramAudit=()=>flows.map(f=>({id:f.id,length:f.length,count:f.count,color:f.color,kind:f.kind,start:f.route.getPointAtLength(0).toJSON?.()||{x:f.route.getPointAtLength(0).x,y:f.route.getPointAtLength(0).y},end:{x:f.route.getPointAtLength(f.length).x,y:f.route.getPointAtLength(f.length).y}}));
  let paused=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let current=0, previous=null;
  const toggle=document.querySelector('#toggle');
  toggle.textContent=paused?'Avvia':'Pausa';
  toggle.addEventListener('click',()=>{paused=!paused;toggle.textContent=paused?'Avvia':'Pausa';previous=null;});
  document.querySelector('#size').addEventListener('click',e=>{const full=document.querySelector('.stage').classList.toggle('full-size');e.currentTarget.textContent=full?'Adatta alla finestra':'Dimensione originale';});
  window.pauseDiagram=()=>{paused=true;toggle.textContent='Avvia';};
  function tick(stamp) {if(!paused&&previous!==null)current+=(stamp-previous)/1000;previous=stamp;if(!paused)setFrame(current);requestAnimationFrame(tick);}
  setFrame(0);requestAnimationFrame(tick);
})();
