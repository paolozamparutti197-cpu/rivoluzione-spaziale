import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { aggregate, validate } from '../archivio/spacex/core.js';
import { applyWikipediaCorrections } from './correzioni_archivio_spacex.mjs';
import { updateLaunchSummary } from './riepilogo_archivio_spacex.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
if (!process.argv[2]) throw Error('Specificare il JSON di importazione prodotto da aggiorna_archivio_spacex.ps1');
const raw = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const directory = path.join(root, 'archivio/spacex');
function save(file,content) {
  if (fs.existsSync(file) && fs.readFileSync(file,'utf8')===content) return;
  const temporary=`${file}.building`;
  fs.writeFileSync(temporary,content);
  // Il cambio di nome evita di troncare una pagina servita o indicizzata su Windows.
  for (let attempt=0;attempt<4;attempt++) {
    try {fs.renameSync(temporary,file);return;}
    catch(error) {if(attempt===3) throw error;Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,150);}
  }
}
const required = ['nr','data','lanciatore','cliente','stato','tipo_record','id_lancio','famiglia_lanciatore'];
if (!raw.launches.length || required.some(k => !(k in raw.launches[0]))) throw Error('Schema elenco cambiato: controllare le intestazioni');
const main = raw.launches.filter(r => r.tipo_record === 'Lancio principale' && !r.id_lancio.startsWith('SIM-'));
const additional = raw.launches.filter(r => r.tipo_record === 'Core/booster aggiuntivo' && !r.id_lancio.startsWith('SIM-'));
const unknownTypes = raw.launches.filter(r => !['Lancio principale','Core/booster aggiuntivo'].includes(r.tipo_record) && !r.id_lancio.startsWith('SIM-'));
if (unknownTypes.length) throw Error('Tipo record sconosciuto');
const source = (sheet, row, book = 'lanci_spacex.xlsx') => `${book} · ${sheet} · riga ${row}`;
const nil = v => v == null || v === '' ? null : v;
const serialOrNull = v => !nil(v) || /^(N\/A|TBD|da confermare)$/i.test(String(v)) ? null : v;
const int = v => nil(v) == null ? null : Number(v);
const corrections = [];
function issue(m, code, text, refs = [m.source]) {
  m.issues.push(text);
  corrections.push({ id: `${m.id}:${code}`, missionId: m.id, date: raw.imported, kind: 'segnalazione', text, sources: refs, action: 'Originali conservati; nessuna sostituzione automatica.' });
}
function mission(r) {
  const m = {
    id: r.id_lancio, name: r.cliente || 'Nome non documentato', date: r.data || r.data_evento,
    family: r.famiglia_lanciatore, launcher: r.lanciatore, scope: r.famiglia_lanciatore === 'Starship' ? (r.fase_programma === 'Operativo' ? 'operational' : 'test') : 'falcon',
    originalPhase: nil(r.fase_programma), class: nil(r.classe_missione), pad: nil(r.dove), padId: nil(r.pad_id), orbit: nil(r.orbita),
    source: source('elenco', r.source_row), sourceRow: r.source_row, references: [...new Set((r.fonti_missione || '').match(/https?:\/\/[^\s;]+/g) || [])],
    sourceNote: nil(r.fonti_missione), video: nil(r.video_url), notes: r.note_missione || '', issues: [],
    programFlight: int(r.volo_programma),
    attempt: { id: `${r.id_lancio}:decollo`, missionId: r.id_lancio, status: 'decollato', ordinal: null, cancelledAttempts: null },
    launch: { id: `${r.id_lancio}:lancio`, missionId: r.id_lancio, attemptId: `${r.id_lancio}:decollo`, outcome: nil(r.stato), timeUTC: nil(r.ora_utc) },
    payload: { outcome: nil(r.esito_payload), count: int(r.numero_payload), description: r.cliente, source: source('elenco', r.source_row) }, flights: [],
  };
  if (!m.payload.outcome) issue(m, 'payload-mancante', 'Esito del carico non documentato separatamente.');
  if (/attesa di conferma|indicazione di Paolo/i.test(m.notes)) issue(m, 'conferma-pendente', 'Successo generale registrato su indicazione dell’utente; conferma ufficiale del rilascio ancora pendente.');
  if (/\uFFFD/.test(m.name + m.notes)) issue(m, 'testo-originale', 'Caratteri danneggiati nel testo originale, conservati senza ricostruzione.');
  return m;
}
function falconFlight(m, r, role) {
  const landing = nil(r.landing);
  const ordinalValue = int(r.voli);
  const v = { id: `${m.id}:${role}`, launchId: m.launch.id, role, serial: serialOrNull(r.booster), serialOriginal: nil(r.booster), ordinal: Number.isInteger(ordinalValue) && ordinalValue > 0 ? ordinalValue : null, ordinalOriginal: nil(r.voli),
    source: source('elenco', r.source_row), sourceRow: r.source_row,
    recovery: { id: `${m.id}:${role}:recupero`, attempt: landing ? int(r.tentativo_recupero) : null, landed: landing ? int(r.recupero_riuscito) : null,
      physical: null, mode: landing, notes: 'Flag di atterraggio del registro. Recupero fisico e sopravvivenza durante il trasporto non documentati separatamente.' } };
  if (!v.serial) issue(m, `matricola-${role}`, `Matricola mancante per ${role}; la posizione non conta come veicolo identificato.`);
  if (!v.ordinal) issue(m, `progressivo-${role}`, `Numero del volo non documentato per ${role}.`);
  if (r.voli != null && v.ordinal == null) issue(m, `progressivo-invalido-${role}`, `Progressivo originale «${r.voli}» non interpretabile come numero intero positivo; valore normalizzato non disponibile.`);
  if (r.booster_riutilizzato === 1 && v.ordinal == null) issue(m, `riuso-senza-progressivo-${role}`, 'Il flag originale indica riutilizzo ma manca un progressivo interpretabile. Il record non entra nei reflight documentati.');
  if (!landing) issue(m, `recupero-${role}`, `Recupero non documentato per ${role}.`);
  // Le sigle non previste richiedono una revisione; non vengono convertite in successo.
  const recognized = /^(OCISLY|JRTI|ASOG|RTLS|LZ-4|LZ-40|EXP|N\/A|WL|PCL|TAD)( \(fallito\))?$/.test(landing || '');
  if (landing && !recognized) issue(m, `sigla-${role}`, `Sigla landing non riconosciuta: ${landing}. Flag originali conservati.`);
  return v;
}
const missions = main.map(mission);
const amosSource = 'https://sma.nasa.gov/LaunchVehicle/assets/anomaly-updates-spacex.pdf';
for (const m of missions) if (m.id === 'SX-0034' && /^Amos[ -]?6$/i.test(m.name) && m.date === '2016-09-01') {
  m.launch.id = null; m.launch.originalOutcome = m.launch.outcome; m.launch.outcome = null;
  m.attempt.status = 'evento a terra prima del decollo';
  m.notes = 'Perdita del veicolo e del carico durante le operazioni di prova statica pre-lancio. Nessun decollo avvenuto. Il registro originale lo classifica come lancio fallito; questa fotografia lo conserva come evento pre-lancio.';
  m.references.push(amosSource);
  issue(m, 'evento-prelancio', 'Amos-6: prova a terra, esclusa dal numero dei decolli. La riga originale resta conservata.', [m.source, amosSource]);
  corrections.at(-1).kind = 'correzione documentata';
  corrections.at(-1).action = 'Nella nuova vista: nessun lancio né volo di booster. Registro originale invariato.';
}
for (const m of missions) {
  const r = main.find(r => r.id_lancio === m.id);
  if (m.family === 'Starship' || !m.launch.id) continue;
  m.flights.push(falconFlight(m, r, m.family === 'Falcon Heavy' ? 'centrale' : 'booster'));
  const extras = additional.filter(r => r.id_lancio === m.id);
  if (m.family === 'Falcon Heavy') {
    if (extras.length !== 2) throw Error(`Due laterali richiesti per ${m.id}; trovati ${extras.length}`);
    extras.forEach((r, i) => m.flights.push(falconFlight(m, r, `laterale ${i ? 'B' : 'A'}`)));
  } else if (extras.length) throw Error(`Riga aggiuntiva non Falcon Heavy: ${m.id}`);
}
for (const r of additional) if (!missions.some(m => m.id === r.id_lancio)) throw Error(`Booster orfano: ${r.id_lancio}`);
for (const t of raw.tests) {
  const flight = Number(t.Flight.match(/\d+/)?.[0]);
  if (!flight) throw Error('Numero prova mancante');
  const mono = raw.monograph.find(r => r.numero === flight);
  if (!mono) throw Error(`Registro monografia senza Flight ${flight}`);
  const dateParts = String(t.Data).match(/^(\d{2})\/(\d{2})\/(\d{4})/);
  const excelDate = dateParts ? `${dateParts[3]}-${dateParts[2]}-${dateParts[1]}` : null;
  let m = missions.find(m => m.family === 'Starship' && m.programFlight === flight);
  if (!m) {
    const id = `IFT-${String(flight).padStart(2, '0')}`;
    m = mission({ id_lancio: id, cliente: `Starship Flight ${flight}`, data: excelDate || mono.data,
      famiglia_lanciatore: 'Starship', lanciatore: `Starship / Super Heavy ${t.Block}`, fase_programma: 'Prova integrata',
      classe_missione: 'Prova integrata', volo_programma: flight, stato: null, source_row: t.source_row });
    m.source = source('Voli integrati', t.source_row, 'sviluppo_starship.xlsx');
    m.payload.source = m.source;
    m.issues = []; // Per le prove un esito globale comparabile ai lanci operativi non viene inventato.
    corrections.splice(corrections.findIndex(c => c.missionId === id), corrections.filter(c => c.missionId === id).length);
    m.scope = 'test';
    m.payload.description = mono.carico;
    m.orbit = mono.profilo;
    m.notes = t.Lezione || '';
    missions.push(m);
  } else {
    corrections.push({ id: `${m.id}:unione-registri`, missionId: m.id, date: raw.imported, kind: 'normalizzazione', text: `Flight ${flight} presente in due registri: un solo lancio operativo, secondo la fase del registro principale.`, sources: [m.source, source('Voli integrati', t.source_row, 'sviluppo_starship.xlsx')], action: 'Unione per numero di volo, data e famiglia. Le note di sviluppo restano consultabili nella stessa scheda.' });
  }
  m.development = { source: source('Voli integrati', t.source_row, 'sviluppo_starship.xlsx'), rawOutcome: t['Esito integrato'], vehicle: t.Veicolo,
    booster: t.Booster, ship: t.Ship, milestone: t.Milestone, monograph: mono, monographSource: `monografie/starship/voli.json · numero ${flight}` };
  if (excelDate && excelDate !== mono.data || excelDate && excelDate !== m.date) issue(m, 'data-divergente', 'Le date dei registri non coincidono.', [m.source, m.development.source, m.development.monographSource]);
  if (!m.launch.timeUTC) m.launch.timeUTC = String(t.Data).match(/(\d{2}:\d{2}(?::\d{2})?) UTC/)?.[1] || null;
  const serialMatch = String(t.Veicolo).match(/Booster (\d+)(?:-(\d+))? \+ Ship (\d+)/);
  if (!serialMatch) throw Error(`Matricole prova non riconosciute: ${t.Veicolo}`);
  for (const [role, serial, ordinal, note] of [['Super Heavy', `B${serialMatch[1]}`, serialMatch[2] ? Number(serialMatch[2]) : null, t.Booster], ['Ship', `S${serialMatch[3]}`, null, t.Ship]]) {
    const rec = raw.recoveries.find(r => r.id_lancio === m.id && r.ruolo === role);
    const catchSuccess = role === 'Super Heavy' && /Catch riuscito/i.test(note);
    const recoveryShip = role === 'Ship' && /Recovery.*riuscita/i.test(t.Lezione || '');
    const v = { id: `${m.id}:${role}`, launchId: m.launch.id, role, serial: rec?.veicolo || serial, ordinal: rec ? int(rec.volo_veicolo) : ordinal,
      source: rec ? source('recuperi_veicoli', rec.source_row) : m.development.source,
      recovery: { id: `${m.id}:${role}:recupero`, attempt: rec ? int(rec.tentativo_recupero_num) : catchSuccess ? 1 : null,
        landed: rec ? int(rec.recuperato_num) : catchSuccess ? 1 : null,
        physical: rec ? (/^s[iì]$/i.test(rec.recupero_fisico || '') ? 1 : /^no$/i.test(rec.recupero_fisico || '') ? 0 : null) : catchSuccess || recoveryShip ? 1 : null,
        mode: rec?.modalita_effettiva || null, notes: rec?.note || (recoveryShip ? `${note} ${t.Lezione}` : note), recoveryDate: rec?.data_recupero || null,
        reference: rec?.fonte_url || null } };
    m.flights.push(v);
  }
  if ([4,6,12,13,14].includes(flight)) issue(m, 'descrizioni-divergenti', 'I registri usano descrizioni o criteri di esito differenti. Leggere i testi affiancati; nessun esito sperimentale è trasformato in successo operativo.', [m.source, m.development.source, m.development.monographSource]);
}
if (raw.monograph.some(r => !missions.some(m => m.programFlight === r.numero && m.family === 'Starship'))) throw Error('Volo monografia non riconciliato');
if (raw.recoveries.some(r => !missions.some(m => m.id === r.id_lancio))) throw Error('Recupero senza missione');
const wikipediaPath = path.join(directory,'correzioni-wikipedia.json');
const wikipediaReview = JSON.parse(fs.readFileSync(wikipediaPath,'utf8'));
const appliedCorrections = applyWikipediaCorrections(missions,wikipediaReview);
// Una lacuna dell'originale colmata dalla revisione non resta una lacuna corrente.
for (let i=corrections.length-1;i>=0;i--) {
  const c=corrections[i],m=missions.find(m=>m.id===c.missionId);
  const resolved=m?.flights.some(v=>
    (c.id===`${m.id}:matricola-${v.role}` && v.serial) ||
    ([`progressivo-${v.role}`,`progressivo-invalido-${v.role}`,`riuso-senza-progressivo-${v.role}`].some(code=>c.id===`${m.id}:${code}`) && v.ordinal) ||
    (c.id===`${m.id}:recupero-${v.role}` && v.recovery.attempt!=null));
  if (resolved) {m.issues=m.issues.filter(x=>x!==c.text);corrections.splice(i,1);}
}
corrections.push(...appliedCorrections);
missions.sort((a,b) => a.date.localeCompare(b.date) || (a.wikipedia?.timeUTC || a.launch.timeUTC || '').localeCompare(b.wikipedia?.timeUTC || b.launch.timeUTC || '') || a.id.localeCompare(b.id));
const seen = new Map();
for (const m of missions) for (const v of m.flights) {
  if (!v.serial || !v.ordinal) continue;
  const previous = seen.get(v.serial);
  if (previous && v.ordinal <= previous.ordinal) issue(m, `progressivo-anomalo-${v.role}`, `Progressivo ${v.ordinal} di ${v.serial} non superiore al precedente ${previous.ordinal} (${previous.mission}). Valori originali conservati.`, [v.source, previous.source]);
  seen.set(v.serial, { ordinal: v.ordinal, mission: m.id, source: v.source });
}
const data = { schemaVersion: 1, imported: raw.imported, coverageEnd: missions.at(-1).date, wikipedia: {date:wikipediaReview.date,...wikipediaReview.summary},
  sources: Object.entries(raw.hashes).map(([file, sha256]) => ({ file, sha256 })),
  coverage: { principal: main.length, principalLaunches: missions.filter(m=>main.some(r=>r.id_lancio===m.id)&&m.launch.id).length, prelaunchEvents: missions.filter(m=>!m.launch.id).length,
    starshipOverlap: main.filter(r=>r.famiglia_lanciatore==='Starship'&&raw.tests.some(t=>Number(String(t.Flight).match(/\d+/)?.[0])===r.volo_programma)).length,
    additional: additional.length, starshipTests: raw.tests.length, cancelledAttempts: 'non documentati sistematicamente', prototypeHops: 'fuori dal perimetro' },
  vehicles: [...new Set(missions.flatMap(m => m.flights.map(v => v.serial)).filter(Boolean))].sort().map(serial => ({ id: serial, serial })), missions };
const errors = validate(data);
if (errors.length) throw Error(errors.join('\n'));
const legacyMetrics = [...raw.legacy_html.matchAll(/<div class="metric"><b>([^<]+)<\/b><span>([^<]+)<\/span><\/div>/g)].map(x => ({ label: x[2], value: x[1] }));
const registerTotal = aggregate(missions.filter(m => main.some(r => r.id_lancio === m.id)));
const controls = [
  ['lanci principali', registerTotal.launches], ['successi', registerTotal.launchSuccess],
  ['atterraggi booster', registerTotal.landingSuccess],
];
const checks = controls.map(([label, value]) => {const site=Number(legacyMetrics.find(x=>x.label===label || label==='atterraggi booster'&&x.label==='recuperi booster')?.value ?? NaN);return {label,workbook:value,correctedArchive:value,site,matches:site===value};});
const report = { date: raw.imported, schemaErrors: errors, sourceCounts: data.coverage, statistics: aggregate(missions), legacyComparison: checks, wikipedia: wikipediaReview.summary,
  legacyNotes: ['Il sito storico espone riepiloghi, non tutte le righe: confronto di totali e ultima missione, non una verifica riga per riga.', '613 è la somma del flag Excel booster_riutilizzato: i reflight con progressivo noto sono un conteggio distinto.', 'Il generico successo del lancio non viene usato per riempire gli esiti payload mancanti.'],
  workbookFlags: { recoveryAttempts: raw.launches.reduce((n,r) => n + (r.tentativo_recupero === 1 ? 1 : 0), 0), landingSuccess: raw.launches.reduce((n,r) => n + (r.recupero_riuscito === 1 ? 1 : 0), 0), reflightFlags: raw.launches.reduce((n,r) => n + (r.booster_riutilizzato === 1 ? 1 : 0), 0) },
  findings: corrections };
report.principalStatistics = registerTotal;
const latest = [...main].sort((a,b)=>String(a.data).localeCompare(String(b.data))||a.nr-b.nr).at(-1);
const legacyLatest = raw.legacy_html.match(/<article class="next-launch history-latest">[\s\S]*?<h3>(.*?)<\/h3>[\s\S]*?<p>(\d{2})\/(\d{2})\/(\d{4}) · lancio SpaceX #(\d+)<\/p>/);
const correctedLatest = raw.legacy_html.match(/<article class="next-launch history-latest">[\s\S]*?<h3>(.*?)<\/h3>[\s\S]*?<p>(\d{2})\/(\d{2})\/(\d{4}) · identificativo (SX-\d+)<\/p>/);
report.latestComparison = { workbook: { id: latest.id_lancio, date: latest.data, name: latest.cliente }, site: legacyLatest ? { date:`${legacyLatest[4]}-${legacyLatest[3]}-${legacyLatest[2]}`, name:legacyLatest[1].replaceAll('&amp;','&'), number:Number(legacyLatest[5]) } : null,
  matches: !!legacyLatest && `${legacyLatest[4]}-${legacyLatest[3]}-${legacyLatest[2]}`===latest.data && legacyLatest[1].replaceAll('&amp;','&')===latest.cliente && Number(legacyLatest[5])===latest.nr };
if (correctedLatest) {
  report.latestComparison.site={date:`${correctedLatest[4]}-${correctedLatest[3]}-${correctedLatest[2]}`,name:correctedLatest[1].replaceAll('&amp;','&'),id:correctedLatest[5]};
  report.latestComparison.matches=report.latestComparison.site.date===latest.data&&report.latestComparison.site.name===latest.cliente&&report.latestComparison.site.id===latest.id_lancio;
}
const oldLogPath = path.join(directory,'registro-correzioni.json');
const oldLog = fs.existsSync(oldLogPath) ? JSON.parse(fs.readFileSync(oldLogPath,'utf8')) : [];
const keyOf = r => `${r.id}|${r.text}`;
const mergedLog = oldLog.map(r=>({...r,status:'risolta'}));
for (const r of corrections) {
  const previous = mergedLog.find(x=>keyOf(x) === keyOf(r));
  if (previous) { previous.status = 'presente'; previous.lastSeen = raw.imported; }
  else mergedLog.push({...r,status:'presente',lastSeen:raw.imported});
}
const snapshots = { date: raw.imported, sources: data.sources, launches: raw.launches, recoveries: raw.recoveries, tests: raw.tests, monograph: raw.monograph, sites: raw.sites };
fs.mkdirSync(directory, { recursive: true });
// Scrittura solo dopo la validazione dell'intero import.
for (const [name, payload] of [['dati.json',data],['registro-correzioni.json',mergedLog],['riconciliazione.json',report],['fonti-snapshot.json',snapshots]]) save(path.join(directory,name), JSON.stringify(payload, null, 2) + '\n');
const escape = x => String(x ?? 'Non documentato').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const fmt = x => x == null ? 'Non documentato' : escape(x);
const header = `<a class="skip" href="#contenuto">Vai al contenuto</a><header><a class="brand" href="../../../index.html">Rivoluzione Spaziale</a><nav aria-label="Navigazione"><a href="../index.html">Archivio</a><a href="../metodo.html">Metodo e fonti</a><a href="../../../sezioni/monografie-spacex.html">Monografie</a></nav></header>`;
const cardsDir = path.join(directory,'missioni');
fs.mkdirSync(cardsDir,{recursive:true});
for (const m of missions) {
  const flights = m.flights.map(v => `<article class="vehicle"><h3>${escape(v.role)} · ${fmt(v.serial)}</h3><dl><dt>Volo progressivo</dt><dd>${fmt(v.ordinal)}</dd><dt>Tentativo di recupero</dt><dd>${v.recovery.attempt == null ? 'Non documentato' : v.recovery.attempt ? 'Sì' : 'No'}</dd><dt>Atterraggio/cattura riuscito</dt><dd>${v.recovery.landed == null ? 'Non documentato' : v.recovery.landed ? 'Sì' : 'No'}</dd><dt>Recupero fisico attestato</dt><dd>${v.recovery.physical == null ? 'Non documentato separatamente' : v.recovery.physical ? 'Sì' : 'No'}</dd><dt>Landing originale</dt><dd>${fmt(v.recovery.mode)}</dd></dl><p>${escape(v.recovery.notes)}</p><p class="source">${escape(v.source)}</p></article>`).join('');
  const development = m.development ? `<section><h2>I registri del volo ${m.programFlight}</h2><div class="two"><article class="panel"><h3>Excel sviluppo</h3><p>Esito originale: ${escape(m.development.rawOutcome)}</p><p>Booster: ${escape(m.development.booster)}</p><p>Ship: ${escape(m.development.ship)}</p><p>${escape(m.development.milestone)}</p><p class="source">${escape(m.development.source)}</p></article><article class="panel"><h3>Registro della monografia</h3><p>Profilo: ${escape(m.development.monograph.profilo)}</p><p>Booster: ${escape(m.development.monograph.booster)}</p><p>Ship: ${escape(m.development.monograph.ship)}</p><p>Carico: ${escape(m.development.monograph.carico)}</p><p>${escape(m.development.monograph.nota)}</p><a href="../../../monografie/starship/18-registro.html">Registro Starship</a><p class="source">${escape(m.development.monographSource)}</p></article></div></section>` : '';
  const issueSection = m.issues.length ? `<section class="warning"><h2>Dati mancanti e divergenze</h2><ul>${m.issues.map(x=>`<li>${escape(x)}</li>`).join('')}</ul></section>` : '';
  save(path.join(cardsDir,`${m.id}.html`), `<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(m.name)} | Archivio SpaceX</title><link rel="stylesheet" href="../archivio.css"></head><body>${header}<main id="contenuto"><p class="eyebrow">Scheda missione · ${escape(m.id)}</p><h1>${escape(m.name)}</h1><p class="lede">${m.date} · ${escape(m.launcher)} · ${escape(m.pad || 'Pad non documentato')}</p><a class="button" href="../index.html?q=${encodeURIComponent(m.id)}&scope=all">Consulta nel contesto dell’archivio</a><section class="panel"><h2>Missione, lancio e carico</h2><dl><dt>Perimetro di consultazione</dt><dd>${m.scope === 'test' ? 'Prova integrata' : m.scope === 'operational' ? 'Starship operativa nel registro principale' : 'Registro principale Falcon'}</dd><dt>Fase nel registro originale</dt><dd>${fmt(m.originalPhase)}</dd><dt>Esito generale del lancio</dt><dd>${m.launch.id ? fmt(m.launch.outcome) : 'Nessun decollo (evento pre-lancio)'}${m.scope === 'test' ? ' (prove sperimentali valutate separatamente)' : ''}</dd><dt>Esito del carico</dt><dd>${fmt(m.payload.outcome)}</dd><dt>Numero payload</dt><dd>${fmt(m.payload.count)}</dd><dt>Orbita / profilo</dt><dd>${fmt(m.orbit)}</dd><dt>Ora UTC documentata</dt><dd>${fmt(m.launch.timeUTC)}</dd><dt>Tentativo documentato</dt><dd>${m.launch.id ? 'Decollo avvenuto. Numero di tentativi precedenti non documentato.' : 'Evento a terra, prima del decollo. Nessun lancio avvenuto.'}</dd></dl><p>${escape(m.notes)}</p><p class="source">${escape(m.source)}. Fotografia importata il ${raw.imported}. La fotografia Excel conserva i valori originali. Per le missioni verificate, la data pubblicata segue il giorno UTC riportato da Wikipedia.</p></section><section><h2>Veicoli e recupero</h2><div class="vehicles">${flights}</div>${m.family === 'Falcon Heavy' ? '<p>A e B indicano l’ordine delle righe, non il lato fisico del lanciatore. Questa scheda conta un solo lancio.</p>' : ''}</section>${development}${issueSection}${m.wikipedia ? `<section class="panel"><h2>Verifica con Wikipedia</h2><p>Confronto del ${m.wikipedia.checked}: ${escape(m.wikipedia.fieldsChecked.join(", "))}. Data UTC: ${m.wikipedia.dateUTC}${m.wikipedia.timeUTC ? ` · ${m.wikipedia.timeUTC} UTC (precisione della tabella)` : ""}.</p><a href="${escape(m.wikipedia.source)}">Tabella Wikipedia utilizzata</a> · <a href="../verifica-wikipedia.html">Valori prima e dopo la revisione</a></section>` : ""}<section class="panel"><h2>Provenienza e riferimenti</h2><p>${escape(m.sourceNote || 'Non sono presenti fonti web individuali nel registro principale.')}</p><ul>${m.references.map((u,i)=>`<li><a href="${escape(u)}">Riferimento ${i+1}: ${escape(new URL(u).hostname)}</a></li>`).join('')}</ul><p>Le fonti del registro sono integrate con il confronto Wikipedia, dove attestato nel riquadro di verifica. La conferma ufficiale del singolo payload resta distinta.</p><a href="../metodo.html">Definizioni, formule e riconciliazione</a></section></main><footer>Archivio SpaceX · Importazione ${raw.imported}</footer></body></html>\n`);
}
// Indice statico: le schede restano raggiungibili anche senza JavaScript.
function writeList(filename,title,selected,intro) {
  const rows=[...selected].reverse().map(m=>`<tr><td>${m.date}</td><td><a href="missioni/${escape(m.id)}.html">${escape(m.name)}</a></td><td>${escape(m.id)}</td><td>${escape(m.family)}</td></tr>`).join('');
  save(path.join(directory,filename),`<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title} | Archivio SpaceX</title><link rel="stylesheet" href="archivio.css"></head><body><header><a class="brand" href="../../index.html">Rivoluzione Spaziale</a><nav aria-label="Navigazione"><a href="index.html">Archivio</a><a href="metodo.html">Metodo e fonti</a></nav></header><main><p class="eyebrow">Indice statico delle schede</p><h1>${title}</h1><p>${intro}</p><p><a href="elenco.html">Lanci operativi</a> · <a href="prove-starship.html">Prove Starship</a> · <a href="eventi-prelancio.html">Eventi a terra</a> · <a href="verifica-wikipedia.html">Confronto Wikipedia</a></p><div class="table-scroll"><table><thead><tr><th>Data UTC</th><th>Missione</th><th>ID</th><th>Famiglia</th></tr></thead><tbody>${rows}</tbody></table></div></main><footer>Archivio SpaceX · Importazione ${raw.imported}</footer></body></html>\n`);
}
const operational=missions.filter(m=>m.launch.id&&m.scope!=='test');
writeList('elenco.html','Elenco dei lanci operativi',operational,`${operational.length} decolli. Falcon 1, Falcon 9, Falcon Heavy e soltanto Starship classificata Operativo nel registro principale. Le prove integrate e gli eventi a terra sono separati. Date UTC secondo la revisione Wikipedia, con originali conservati.`);
writeList('prove-starship.html','Prove integrate Starship',missions.filter(m=>m.scope==='test'),`Le prove sono escluse dall’elenco dei lanci operativi. Il volo 14 compare una sola volta, nel registro operativo. Le date seguono i registri di sviluppo originali.`);
writeList('eventi-prelancio.html','Eventi prima del decollo',missions.filter(m=>!m.launch.id),'Eventi a terra documentati nel registro originale. Non contano come lanci né come voli di booster.');
const reviewedRows=wikipediaReview.patches.map(p=>`<tr><td><a href="missioni/${escape(p.missionId)}.html">${escape(p.missionId)}</a></td><td>${escape(p.field)}</td><td>${escape(JSON.stringify(p.before))}</td><td>${escape(JSON.stringify(p.after))}${p.reason ? `<p class="source">${escape(p.reason)}</p>` : ''}</td><td><a href="${escape(p.source)}">Wikipedia</a>${(p.references||[]).map(u=>` · <a href="${escape(u)}">${escape(new URL(u).hostname)}</a>`).join('')}</td></tr>`).join('');
save(path.join(directory,'verifica-wikipedia.html'),`<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Verifica Wikipedia | Archivio SpaceX</title><link rel="stylesheet" href="archivio.css"></head><body><header><a class="brand" href="../../index.html">Rivoluzione Spaziale</a><nav aria-label="Navigazione"><a href="index.html">Archivio</a><a href="metodo.html">Metodo e fonti</a></nav></header><main><p class="eyebrow">Verifica del ${wikipediaReview.date}</p><h1>Confronto dell’elenco operativo con Wikipedia</h1><p class="lede">${wikipediaReview.summary.matchedLaunches} decolli abbinati uno a uno: 5 Falcon 1, 693 Falcon 9, 14 Falcon Heavy e un volo operativo Starship. Nessuna missione mancante nei due elenchi, entro questa copertura.</p><section class="panel"><h2>Perimetro e metodo</h2><p>${escape(wikipediaReview.scope)}</p><p>${escape(wikipediaReview.method)}</p><p>Le tabelle delle missioni, aggiornate anche al 10 ottobre, prevalgono sui riepiloghi introduttivi di Wikipedia rimasti al 2 ottobre. I conteggi di recupero non sono confrontati senza uniformare il criterio: contatto al suolo, ammaraggio controllato e veicolo integro dopo il trasporto sono risultati distinti.</p><p>${wikipediaReview.summary.correctedMissions} schede corrette; ${wikipediaReview.summary.correctedFields} campi rivisti. Le denominazioni abbreviate equivalenti rimangono quelle del registro.</p><a href="correzioni-wikipedia.json" download>Scarica abbinamenti, correzioni e impronte delle fonti</a> · <a href="elenco.html">Lanci operativi</a> · <a href="prove-starship.html">Prove Starship separate</a></section><section><h2>Fonti consultate</h2><ul>${wikipediaReview.sources.map(s=>`<li><a href="${escape(s.url)}">${escape(decodeURIComponent(s.url.split('/wiki/')[1]).replaceAll('_',' '))}</a> · consultata ${s.retrieved}</li>`).join('')}</ul></section><section><h2>Valori originali e correzioni applicate</h2><p>Le colonne originali provengono dalla fotografia dei registri. Le correzioni sono applicate al sito senza modificare gli Excel né i gestori Python.</p><div class="table-scroll"><table><thead><tr><th>Missione</th><th>Campo</th><th>Originale</th><th>Sito corretto</th><th>Fonte</th></tr></thead><tbody>${reviewedRows}</tbody></table></div></section></main><footer>Archivio SpaceX · Revisione documentata</footer></body></html>\n`);
updateLaunchSummary(root,data);
console.log(JSON.stringify({ missions: missions.length, principal: main.length, additional: additional.length, vehicles: data.vehicles.length, corrections: corrections.length, checks }, null, 2));
