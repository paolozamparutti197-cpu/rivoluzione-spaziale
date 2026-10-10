import fs from 'node:fs';
import path from 'node:path';
import {aggregate,annualSeries,filterMissions} from '../archivio/spacex/core.js';
const esc=x=>String(x??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
export function updateLaunchSummary(root,data) {
  const main=filterMissions(data.missions),stats=aggregate(main),latest=main.at(-1);
  const family=[...new Set(main.map(m=>m.family))].map(name=>({name,count:main.filter(m=>m.family===name).length}));
  const pads=[...new Set(main.map(m=>m.pad))].map(name=>({name:name||'Non documentato',count:main.filter(m=>m.pad===name).length})).sort((a,b)=>b.count-a.count);
  const bars=(values,max)=>values.map(v=>`<div class="summary-bar"><span>${esc(v.name)}</span><div><i style="width:${100*v.count/max}%"></i></div><b>${v.count}</b></div>`).join('');
  const file=path.join(root,'sezioni/storico-lanci.html');
  const original=fs.readFileSync(file,'utf8');
  const before=original.slice(0,original.indexOf('<main'));
  const after=original.slice(original.lastIndexOf('</main>')+7);
  const heading=before.includes('archivio/spacex/archivio.css')?before:before.replace('</head>','<link rel="stylesheet" href="../archivio/spacex/archivio.css">\n</head>');
  const body=`<main id="contenuto" class="history-summary"><section class="hero"><div><p class="eyebrow">Registro operativo SpaceX · verifica ${data.imported}</p><h1>Storico lanci</h1><p class="lede">${stats.launches} decolli: Falcon 1, Falcon 9, Falcon Heavy e soltanto Starship classificata operativa. Date espresse in UTC.</p><p>Le 13 prove integrate Starship sono consultabili nel registro sperimentale. Amos-6 resta documentato come evento a terra.</p><a class="button" href="../archivio/spacex/index.html">Consulta e filtra tutti i lanci</a> <a href="../archivio/spacex/elenco.html">Elenco completo</a></div><figure><img src="../monografie/crew-dragon/assets/demo2-decollo.jpg" alt="Decollo di Falcon 9 con Crew Dragon Demo-2, 30 maggio 2020."><figcaption>Demo-2 · NASA/Bill Ingalls.</figcaption></figure></section>
<section><h2>I numeri del registro operativo</h2><div class="metrics">${[[stats.launches,'lanci principali'],[stats.launchSuccess,'successi'],[`${(100*stats.launchSuccess/stats.launchDecided).toFixed(1)}%`,'tasso successo'],[Math.max(...main.flatMap(m=>m.flights.map(v=>v.ordinal||0))),'max voli booster'],[family.find(v=>v.name==='Falcon Heavy')?.count||0,'Falcon Heavy'],[pads.length,'siti di lancio storici'],[stats.landingSuccess,'atterraggi booster'],[stats.reflights,'reflight documentati']].map(([value,label])=>`<div class="metric"><b>${value}</b><span>${label}</span></div>`).join('')}</div><p class="source">Il successo generale usa ${stats.launchDecided} esiti noti. CRS-1 è parziale: Dragon riuscito, carico secondario Orbcomm nell’orbita errata. Gli atterraggi comprendono i contatti riusciti seguiti dalla perdita del veicolo durante il trasporto; non attestano tutti un recupero fisico. Reflight: progressivo maggiore di uno, non somma del flag originale Excel.</p></section>
<section class="panel"><h2>Ultimo lancio registrato</h2><article class="next-launch history-latest"><h3>${esc(latest.name)}</h3><p>${latest.date.split('-').reverse().join('/')} · identificativo ${latest.id}</p><p>${esc(latest.launcher)} · ${esc(latest.pad)} · esito ${esc(latest.launch.outcome)}</p><a href="../archivio/spacex/missioni/${latest.id}.html">Fonti e scheda missione</a></article></section>
<section><h2>Cadenza annuale</h2><p class="source">Il 2026 è aggiornato al ${data.coverageEnd}; nessuna proiezione a fine anno. Un Falcon Heavy conta un decollo.</p><div class="table-scroll"><table><thead><tr><th>Anno</th><th>Decolli</th><th>Successi completi</th></tr></thead><tbody>${annualSeries(main).map(y=>`<tr><td>${y.year}</td><td>${y.launches}</td><td>${y.launchSuccess}</td></tr>`).join('')}</tbody></table></div></section>
<section class="two"><article class="panel"><h2>Famiglie dei lanciatori</h2>${bars(family,Math.max(...family.map(v=>v.count)))}</article><article class="panel"><h2>Siti di lancio storici</h2>${bars(pads,Math.max(...pads.map(v=>v.count)))}</article></section>
<section class="panel"><h2>Confronto con Wikipedia</h2><p>Verificati uno a uno 713 decolli nell’edizione del 10 ottobre 2026: 5 Falcon 1, 693 Falcon 9, 14 Falcon Heavy e un volo operativo Starship. La fase operativa di Starship segue il registro dell’utente, senza includere automaticamente le prove riportate da Wikipedia.</p><a href="../archivio/spacex/verifica-wikipedia.html">Correzioni, fonti e valori originali</a> · <a href="../archivio/spacex/metodo.html">Metodo dei conteggi</a></section></main>`;
  fs.writeFileSync(file,heading+body+after);
  const spacexFile=path.join(root,'sezioni/spacex.html');
  let spacex=fs.readFileSync(spacexFile,'utf8');
  for (const [label,value] of [['lanci SpaceX principali',stats.launches],['success rate storico',`${(100*stats.launchSuccess/stats.launchDecided).toFixed(1)}%`],['recuperi booster riusciti',stats.landingSuccess]])
    spacex=spacex.replace(new RegExp(`(<div class="metric"><b>)[^<]+(</b><span>${label}</span></div>)`,'g'),(_,a,b)=>`${a}${value}${b}`);
  fs.writeFileSync(spacexFile,spacex);
}
