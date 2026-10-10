import { filterMissions, aggregate, annualSeries, compareYears, csv, missionRows, flightRows } from './core.js';
const $ = id => document.getElementById(id);
const escape = x => String(x ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const num = n => n.toLocaleString('it-IT');
const pct = (a,b) => b ? `${(100*a/b).toLocaleString('it-IT',{maximumFractionDigits:1})}%` : 'n.d.';
const form = $('filters');
let data, selected = [], filters = {}, page = 0;
const pageSize = 18;
export const definitions = {
  launches: { label:'Lanci', formula:'Numero di identificativi di lancio distinti. Un Falcon Heavy conta un lancio.' },
  launchRate: { label:'Successo generale del lancio', formula:'Successi ÷ esiti generali definiti (successo, parziale, fallito). Le prove senza esito comparabile sono escluse dal denominatore.' },
  boosterFlights: { label:'Voli dei booster', formula:'Partecipazioni dei booster ai lanci. Tre per Falcon Heavy, una per Falcon 1, Falcon 9 e Super Heavy. La Ship è esclusa.' },
  knownBoosters: { label:'Booster identificati', formula:'Matricole distinte presenti nei risultati. Non è il numero di booster attivi.' },
  reflights: { label:'Reflight documentati', formula:'Voli di booster con progressivo documentato > 1. Non conta i veicoli distinti e non usa il flag generico riutilizzato dell’Excel.' },
  landingRate: { label:'Atterraggio / cattura riuscito', formula:'Atterraggi/catture riusciti ÷ tentativi di recupero con esito noto. Gli ammaraggi sperimentali non attestano un recupero fisico.' },
  cargo: { label:'Esiti del carico documentati', formula:'Missioni con esito payload esplicito nel registro. Il successo del lancio non riempie un campo payload vuoto.' },
  physical: { label:'Recuperi fisici attestati', formula:'Record di tutti i veicoli (booster e Ship) con recupero fisico esplicito. Le celle mancanti restano ignote. Il totale è una copertura parziale, non il totale storico dei recuperi.' },
};
function readFilters() { return Object.fromEntries(new FormData(form)); }
function restore() {
  const p = new URLSearchParams(location.search);
  if (p.get('scope') === 'mixed') p.set('scope','starship');
  for (const field of form.elements) if (field.name) field.value = p.get(field.name) ?? (field.name === 'scope' ? 'operational' : field.name === 'event' ? 'launch' : '');
  const sortValue = p.get('sort');
  $('sort').value = ['desc','asc','name'].includes(sortValue) ? sortValue : 'desc';
}
function synchronizeURL() {
  const p = new URLSearchParams();
  for (const [key,value] of Object.entries(filters)) if (value && !(key === 'scope' && value === 'operational') && !(key === 'event' && value === 'launch')) p.set(key,value);
  if ($('sort').value !== 'desc') p.set('sort',$('sort').value);
  history.replaceState(null,'',location.pathname + (p.size ? `?${p}` : '') + location.hash);
}
function download(name, content, type) {
  const blob = new Blob([content],{type});
  const url = URL.createObjectURL(blob), a = document.createElement('a');
  a.href = url; a.download = name; a.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function renderMetrics() {
  const s = aggregate(selected);
  const cards = [
    ['launches',num(s.launches),'Conteggio distinto dei decolli documentati.'],
    ['launchRate',pct(s.launchSuccess,s.launchDecided),`${num(s.launchSuccess)} successi / ${num(s.launchDecided)} esiti noti. ${num(s.launches-s.launchDecided)} esclusi perché non comparabili o mancanti.`],
    ['boosterFlights',num(s.boosterFlights),'Partecipazioni dei booster, incluse le posizioni senza matricola.'],
    ['knownBoosters',num(s.knownBoosters),`${num(s.missingSerial)} partecipazioni senza matricola.`],
    ['reflights',num(s.reflights),`${num(s.ordinalUnknown)} progressivi mancanti, esclusi dai reflight.`],
    ['landingRate',pct(s.landingRateNumerator,s.recoveryDecided),`${num(s.landingRateNumerator)} riusciti / ${num(s.recoveryDecided)} tentativi con esito noto; ${num(s.recoveryUnknown)} record senza informazione sul tentativo.`],
    ['cargo',num(s.payloadDecided),`${num(s.payloadSuccess)} successi payload espliciti; ${num(s.missions-s.payloadDecided)} esiti non documentati.`],
    ['physical',s.physicalKnown ? num(s.physicalRecoveries) : 'n.d.',`${num(s.physicalKnown)} record di veicolo con sì/no esplicito; ${num(selected.flatMap(m=>m.flights).length-s.physicalKnown)} non documentati.`],
  ];
  $('metrics').innerHTML = cards.map(([key,value,note])=>`<article class="metric"><strong>${value}</strong><span>${definitions[key].label}</span>${key === 'physical' ? '<p class="source">Copertura parziale; nessun totale storico ricostruito.</p>' : ''}<details><summary>Formula e copertura</summary><p>${definitions[key].formula}</p><p>${note}</p><p>Perimetro: ricerca corrente. Importazione ${data.imported}. Fonti: elenco e recuperi_veicoli dell’Excel lanci; Voli integrati dell’Excel sviluppo per le prove (foglio «Voli integrati»). Dettaglio di riga nella scheda.</p></details></article>`).join('');
  const scopeName = form.elements.scope.selectedOptions[0]?.textContent || 'Perimetro non valido';
  const context = `Perimetro: ${scopeName}; tutti i filtri sopra applicati. ${selected.length ? `Date dei risultati: ${selected[0].date} / ${selected.at(-1).date}.` : 'Nessuna missione corrispondente.'} Importazione ${data.imported}; copertura fino al ${data.coverageEnd}. Provenienza: registri Excel lanci e sviluppo Starship, registro della monografia. Revisione Wikipedia del ${data.wikipedia.date}: ${data.wikipedia.matchedLaunches} decolli operativi abbinati; originali conservati. Le prove sono escluse da questa revisione.`;
  $('statistics-context').textContent = context;
  document.querySelector('.chart-context').textContent = context;
}
function renderCards() {
  const sorted = [...selected].sort((a,b)=>$('sort').value === 'name' ? a.name.localeCompare(b.name,'it') : ($('sort').value === 'asc' ? 1 : -1)*(a.date.localeCompare(b.date)||a.id.localeCompare(b.id)));
  const pages = Math.max(1,Math.ceil(sorted.length/pageSize));
  page = Math.max(0,Math.min(page,pages-1));
  $('cards').innerHTML = sorted.length ? sorted.slice(page*pageSize,(page+1)*pageSize).map(m=>`<article class="mission-card"><span class="date">${m.date} · ${escape(m.id)}</span><span class="tag">${escape(m.family)}${m.scope === 'test' ? ' · prova' : m.scope === 'operational' ? ' · operativa' : ''}</span><h3 class="name"><a href="missioni/${encodeURIComponent(m.id)}.html">${escape(m.name)}</a></h3><p>${escape(m.pad || 'Pad non documentato')} · ${escape(m.orbit || 'Orbita non documentata')}</p><p>${m.launch.id ? 'Lancio' : 'Evento pre-lancio'}: ${escape(m.launch.outcome || (!m.launch.id ? 'nessun decollo' : m.scope === 'test' ? 'valutazione sperimentale' : 'non documentato'))}</p><p>Carico: ${escape(m.payload.outcome || 'esito non documentato')}</p><p>Booster: ${m.flights.filter(v=>v.role !== 'Ship').map(v=>`${escape(v.serial || 'matricola ignota')}${v.ordinal ? ` (${v.ordinal})` : ''}`).join(', ')}</p>${m.issues.length ? `<p class="gap-note">${m.issues.length} lacune o divergenze nella scheda</p>` : ''}<p class="source">${escape(m.source)}</p></article>`).join('') : '<p class="panel">Nessuna missione corrisponde ai filtri. Amplia il perimetro o azzera la ricerca.</p>';
  $('page').textContent = `Pagina ${page+1} di ${pages}`;
  $('previous').disabled = page === 0;
  $('next').disabled = page === pages-1;
}
function bars(series, key, overlay) {
  const max = Math.max(1,...series.map(s=>s[key]));
  return series.length ? `${overlay ? '<p class="legend"><span><i></i>Voli booster</span><span><i class="green"></i>Reflight noti</span></p>' : ''}${series.map(s=>`<div class="chart-row"><span>${s.year}</span><div class="track" aria-hidden="true"><div class="bar" style="width:${100*s[key]/max}%"></div>${overlay ? `<div class="overlay" style="width:${100*s[overlay]/max}%"></div>` : ''}</div><span>${overlay ? `${s[overlay]} / ` : ''}${s[key]}</span></div>`).join('')}` : '<p>Nessun dato per questi filtri.</p>';
}
function renderCharts() {
  const series = annualSeries(selected);
  $('annual-chart').innerHTML = bars(series,'launches');
  $('reuse-chart').innerHTML = bars(series,'boosterFlights','reflights');
  $('annual-values').innerHTML = series.map(s=>`<tr>${[s.year,s.launches,s.boosterFlights,s.reflights,s.ordinalUnknown,s.launchSuccess,s.launchDecided].map(v=>`<td>${v}</td>`).join('')}</tr>`).join('');
  const months = ['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic'];
  const rows = series.map(s=>({year:s.year,months:months.map((_,i)=>selected.filter(m=>m.launch.id&&m.date.startsWith(`${s.year}-${String(i+1).padStart(2,'0')}`)).length)}));
  const max = Math.max(1,...rows.flatMap(r=>r.months));
  $('monthly-chart').innerHTML = rows.length ? `<table class="month-table"><thead><tr><th>Anno</th>${months.map(m=>`<th>${m}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr><th>${r.year}</th>${r.months.map((v,i)=>{
    const month = `${r.year}-${String(i+1).padStart(2,'0')}`;
    if (month > data.coverageEnd.slice(0,7)) return '<td aria-label="Fuori copertura">n.d.</td>';
    return `<td class="${month === data.coverageEnd.slice(0,7) ? 'partial' : ''}" style="background:rgba(23,97,154,${.06+.5*v/max})" title="${months[i]} ${r.year}: ${v} lanci nei risultati">${v}</td>`;
  }).join('')}</tr>`).join('')}</tbody></table>` : '<p>Nessun dato per questi filtri.</p>';
}
function renderComparison() {
  const [a,b] = compareYears(selected,Number($('year-a').value),Number($('year-b').value),$('same-cutoff').checked,data.coverageEnd);
  if (!a || !b) return;
  const delta = b.launches-a.launches;
  const change = a.launches ? `${delta>0?'+':''}${(100*delta/a.launches).toLocaleString('it-IT',{maximumFractionDigits:1})}%` : 'non disponibile (base zero)';
  $('comparison-context').textContent = `Ricerca corrente; intervalli 01/01/${a.year} – ${a.cutoff} e 01/01/${b.year} – ${b.cutoff}. La copertura si ferma al ${data.coverageEnd}; un anno incompleto non diventa una previsione dell’anno intero. Fonti e importazione: come nei grafici.`;
  $('comparison').innerHTML = `<div class="comparison-grid">${[a,b].map(s=>`<article><span class="year">${s.year}</span><strong>${num(s.launches)}</strong><p>lanci nella selezione</p><p>${num(s.boosterFlights)} voli booster; ${num(s.reflights)} reflight noti</p><p>Successo generale ${pct(s.launchSuccess,s.launchDecided)} (${s.launchSuccess}/${s.launchDecided} esiti noti)</p></article>`).join('')}</div><p>Variazione dei lanci: <b>${delta>0?'+':''}${delta}</b>; ${change}.</p>`;
}
function render() {
  filters = readFilters();
  const invalidRange = filters.from && filters.to && filters.from > filters.to;
  $('filter-warning').hidden = !invalidRange;
  $('filter-warning').textContent = 'La data iniziale è successiva alla data finale. Correggi l’intervallo.';
  selected = invalidRange ? [] : filterMissions(data.missions,filters);
  synchronizeURL();
  $('count').textContent = `${num(selected.length)} missioni corrispondenti`;
  for (const id of ['export-csv','export-json','export-flights','export-series']) $(id).disabled = !selected.length;
  renderMetrics(); renderCards(); renderCharts(); renderComparison();
}
async function initialize() {
  const response = await fetch('dati.json');
  if (!response.ok) throw Error('Dati non disponibili');
  data = await response.json();
  $('freshness').textContent = `Fotografia importata il ${data.imported}. Ultima data registrata: ${data.coverageEnd}. ${num(data.coverage.principal)} record principali (${data.coverage.principalLaunches} decolli e l’evento pre-lancio Amos-6), ${num(data.coverage.additional)} righe booster aggiuntive e ${data.coverage.starshipTests} voli integrati Starship, riconciliati senza doppio conteggio.`;
  for (const key of ['family','pad','class']) {
    const field = form.elements[key];
    for (const value of [...new Set(data.missions.map(m=>m[key]).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'it'))) field.add(new Option(value,value));
  }
  const years = [...new Set(data.missions.map(m=>m.date.slice(0,4)))].sort();
  for (const id of ['year-a','year-b']) for (const year of years) $(id).add(new Option(year,year));
  $('year-a').value = years.at(-2); $('year-b').value = years.at(-1);
  restore(); render();
  let timer;
  form.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>{page=0;render();},180);});
  form.addEventListener('change',()=>{clearTimeout(timer);page=0;render();});
  form.addEventListener('submit',e=>{e.preventDefault();clearTimeout(timer);page=0;render();});
  form.addEventListener('reset',()=>{clearTimeout(timer);setTimeout(()=>{page=0;render();},0);});
  $('sort').addEventListener('change',()=>{page=0;synchronizeURL();renderCards();});
  $('previous').addEventListener('click',()=>{page--;renderCards();$('missioni').scrollIntoView();});
  $('next').addEventListener('click',()=>{page++;renderCards();$('missioni').scrollIntoView();});
  for (const id of ['year-a','year-b','same-cutoff']) $(id).addEventListener('change',renderComparison);
  window.addEventListener('popstate',()=>{restore();page=0;render();});
  $('copy-link').addEventListener('click',async()=>{
    try { await navigator.clipboard.writeText(location.href); $('copy-link').textContent='Ricerca copiata'; }
    catch { $('copy-link').textContent='Copia l’indirizzo dalla barra del browser'; }
  });
  $('export-csv').addEventListener('click',()=>download(`missioni-spacex-${data.imported}.csv`,csv(missionRows(selected)),'text/csv;charset=utf-8'));
  $('export-flights').addEventListener('click',()=>download(`veicoli-recuperi-spacex-${data.imported}.csv`,csv(flightRows(selected)),'text/csv;charset=utf-8'));
  $('export-series').addEventListener('click',()=>download(`serie-annuali-spacex-${data.imported}.csv`,csv(annualSeries(selected)),'text/csv;charset=utf-8'));
  $('export-json').addEventListener('click',()=>download(`ricerca-spacex-${data.imported}.json`,JSON.stringify({ imported:data.imported,coverageEnd:data.coverageEnd,filters,sources:data.sources,statistics:aggregate(selected),definitions,missions:selected },null,2),'application/json'));
}
initialize().catch(error=>{console.error(error);$('error').hidden=false;$('error').textContent='Non è stato possibile caricare l’archivio. Riprova oppure consulta le schede statiche dall’elenco completo.';});
