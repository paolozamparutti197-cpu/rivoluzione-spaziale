import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { aggregate, validate } from '../archivio/spacex/core.js';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
if (!process.argv[2]) throw Error('Specificare il JSON di importazione prodotto da aggiorna_archivio_spacex.ps1');
const raw = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const directory = path.join(root, 'archivio/spacex');
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
    family: r.famiglia_lanciatore, launcher: r.lanciatore, scope: r.famiglia_lanciatore === 'Starship' ? 'mixed' : 'falcon',
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
    corrections.push({ id: `${m.id}:unione-registri`, missionId: m.id, date: raw.imported, kind: 'normalizzazione', text: `Flight ${flight} presente in due registri: un solo lancio; fase mista conservata.`, sources: [m.source, source('Voli integrati', t.source_row, 'sviluppo_starship.xlsx')], action: 'Unione per numero di volo, data e famiglia. Nessuna modifica agli originali.' });
    issue(m, 'fase-mista', 'Classificato Operativo nell’Excel lanci e incluso nel registro di sviluppo: consultabile come fase mista.');
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
missions.sort((a,b) => a.date.localeCompare(b.date) || a.id.localeCompare(b.id));
const seen = new Map();
for (const m of missions) for (const v of m.flights) {
  if (!v.serial || !v.ordinal) continue;
  const previous = seen.get(v.serial);
  if (previous && v.ordinal <= previous.ordinal) issue(m, `progressivo-anomalo-${v.role}`, `Progressivo ${v.ordinal} di ${v.serial} non superiore al precedente ${previous.ordinal} (${previous.mission}). Valori originali conservati.`, [v.source, previous.source]);
  seen.set(v.serial, { ordinal: v.ordinal, mission: m.id, source: v.source });
}
const data = { schemaVersion: 1, imported: raw.imported, coverageEnd: missions.at(-1).date,
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
  ['recuperi booster', registerTotal.landingSuccess],
];
const checks = controls.map(([label, value]) => ({ label, workbook: value, site: Number(legacyMetrics.find(x => x.label === label)?.value ?? NaN), matches: Number(legacyMetrics.find(x => x.label === label)?.value) === value }));
const report = { date: raw.imported, schemaErrors: errors, sourceCounts: data.coverage, statistics: aggregate(missions), legacyComparison: checks,
  legacyNotes: ['Il sito storico espone riepiloghi, non tutte le righe: confronto di totali e ultima missione, non una verifica riga per riga.', '613 è la somma del flag Excel booster_riutilizzato: i reflight con progressivo noto sono un conteggio distinto.', 'Il generico successo del lancio non viene usato per riempire gli esiti payload mancanti.'],
  workbookFlags: { recoveryAttempts: raw.launches.reduce((n,r) => n + (r.tentativo_recupero === 1 ? 1 : 0), 0), landingSuccess: raw.launches.reduce((n,r) => n + (r.recupero_riuscito === 1 ? 1 : 0), 0), reflightFlags: raw.launches.reduce((n,r) => n + (r.booster_riutilizzato === 1 ? 1 : 0), 0) },
  findings: corrections };
report.principalStatistics = registerTotal;
const latest = [...main].sort((a,b)=>String(a.data).localeCompare(String(b.data))||a.nr-b.nr).at(-1);
const legacyLatest = raw.legacy_html.match(/<article class="next-launch history-latest">[\s\S]*?<h3>(.*?)<\/h3>[\s\S]*?<p>(\d{2})\/(\d{2})\/(\d{4}) · lancio SpaceX #(\d+)<\/p>/);
report.latestComparison = { workbook: { id: latest.id_lancio, date: latest.data, name: latest.cliente }, site: legacyLatest ? { date:`${legacyLatest[4]}-${legacyLatest[3]}-${legacyLatest[2]}`, name:legacyLatest[1].replaceAll('&amp;','&'), number:Number(legacyLatest[5]) } : null,
  matches: !!legacyLatest && `${legacyLatest[4]}-${legacyLatest[3]}-${legacyLatest[2]}`===latest.data && legacyLatest[1].replaceAll('&amp;','&')===latest.cliente && Number(legacyLatest[5])===latest.nr };
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
for (const [name, payload] of [['dati.json',data],['registro-correzioni.json',mergedLog],['riconciliazione.json',report],['fonti-snapshot.json',snapshots]]) fs.writeFileSync(path.join(directory,name), JSON.stringify(payload, null, 2) + '\n');
const escape = x => String(x ?? 'Non documentato').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const fmt = x => x == null ? 'Non documentato' : escape(x);
const header = `<a class="skip" href="#contenuto">Vai al contenuto</a><header><a class="brand" href="../../../index.html">Rivoluzione Spaziale</a><nav aria-label="Navigazione"><a href="../index.html">Archivio</a><a href="../metodo.html">Metodo e fonti</a><a href="../../../sezioni/monografie-spacex.html">Monografie</a></nav></header>`;
const cardsDir = path.join(directory,'missioni');
fs.mkdirSync(cardsDir,{recursive:true});
for (const m of missions) {
  const flights = m.flights.map(v => `<article class="vehicle"><h3>${escape(v.role)} · ${fmt(v.serial)}</h3><dl><dt>Volo progressivo</dt><dd>${fmt(v.ordinal)}</dd><dt>Tentativo di recupero</dt><dd>${v.recovery.attempt == null ? 'Non documentato' : v.recovery.attempt ? 'Sì' : 'No'}</dd><dt>Atterraggio/cattura riuscito</dt><dd>${v.recovery.landed == null ? 'Non documentato' : v.recovery.landed ? 'Sì' : 'No'}</dd><dt>Recupero fisico attestato</dt><dd>${v.recovery.physical == null ? 'Non documentato separatamente' : v.recovery.physical ? 'Sì' : 'No'}</dd><dt>Landing originale</dt><dd>${fmt(v.recovery.mode)}</dd></dl><p>${escape(v.recovery.notes)}</p><p class="source">${escape(v.source)}</p></article>`).join('');
  const development = m.development ? `<section><h2>I registri del volo ${m.programFlight}</h2><div class="two"><article class="panel"><h3>Excel sviluppo</h3><p>Esito originale: ${escape(m.development.rawOutcome)}</p><p>Booster: ${escape(m.development.booster)}</p><p>Ship: ${escape(m.development.ship)}</p><p>${escape(m.development.milestone)}</p><p class="source">${escape(m.development.source)}</p></article><article class="panel"><h3>Registro della monografia</h3><p>Profilo: ${escape(m.development.monograph.profilo)}</p><p>Booster: ${escape(m.development.monograph.booster)}</p><p>Ship: ${escape(m.development.monograph.ship)}</p><p>Carico: ${escape(m.development.monograph.carico)}</p><p>${escape(m.development.monograph.nota)}</p><a href="../../../monografie/starship/18-registro.html">Registro Starship</a><p class="source">${escape(m.development.monographSource)}</p></article></div></section>` : '';
  const issueSection = m.issues.length ? `<section class="warning"><h2>Dati mancanti e divergenze</h2><ul>${m.issues.map(x=>`<li>${escape(x)}</li>`).join('')}</ul></section>` : '';
  fs.writeFileSync(path.join(cardsDir,`${m.id}.html`), `<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(m.name)} | Archivio SpaceX</title><link rel="stylesheet" href="../archivio.css"></head><body>${header}<main id="contenuto"><p class="eyebrow">Scheda missione · ${escape(m.id)}</p><h1>${escape(m.name)}</h1><p class="lede">${m.date} · ${escape(m.launcher)} · ${escape(m.pad || 'Pad non documentato')}</p><a class="button" href="../index.html?q=${encodeURIComponent(m.id)}&scope=all">Consulta nel contesto dell’archivio</a><section class="panel"><h2>Missione, lancio e carico</h2><dl><dt>Perimetro di consultazione</dt><dd>${m.scope === 'test' ? 'Prova integrata' : m.scope === 'mixed' ? 'Orbita con carico, fase mista' : 'Registro principale Falcon'}</dd><dt>Fase nel registro originale</dt><dd>${fmt(m.originalPhase)}</dd><dt>Esito generale del lancio</dt><dd>${m.launch.id ? fmt(m.launch.outcome) : 'Nessun decollo (evento pre-lancio)'}${m.scope === 'test' ? ' (prove sperimentali valutate separatamente)' : ''}</dd><dt>Esito del carico</dt><dd>${fmt(m.payload.outcome)}</dd><dt>Numero payload</dt><dd>${fmt(m.payload.count)}</dd><dt>Orbita / profilo</dt><dd>${fmt(m.orbit)}</dd><dt>Ora UTC documentata</dt><dd>${fmt(m.launch.timeUTC)}</dd><dt>Tentativo documentato</dt><dd>${m.launch.id ? 'Decollo avvenuto. Numero di tentativi precedenti non documentato.' : 'Evento a terra, prima del decollo. Nessun lancio avvenuto.'}</dd></dl><p>${escape(m.notes)}</p><p class="source">${escape(m.source)}. Fotografia importata il ${raw.imported}. Data originale conservata; senza orario non si ricostruisce un timestamp UTC.</p></section><section><h2>Veicoli e recupero</h2><div class="vehicles">${flights}</div>${m.family === 'Falcon Heavy' ? '<p>A e B indicano l’ordine delle righe, non il lato fisico del lanciatore. Questa scheda conta un solo lancio.</p>' : ''}</section>${development}${issueSection}<section class="panel"><h2>Provenienza e riferimenti</h2><p>${escape(m.sourceNote || 'Non sono presenti fonti web individuali nel registro principale.')}</p><ul>${m.references.map((u,i)=>`<li><a href="${escape(u)}">Riferimento ${i+1}: ${escape(new URL(u).hostname)}</a></li>`).join('')}</ul><p>I riferimenti sono quelli associati alle fonti locali; non equivalgono a una verifica indipendente effettuata durante questa importazione.</p><a href="../metodo.html">Definizioni, formule e riconciliazione</a></section></main><footer>Archivio SpaceX · Importazione ${raw.imported}</footer></body></html>\n`);
}
// Indice statico: le schede restano raggiungibili anche senza JavaScript.
const staticLinks = [...missions].reverse().map(m=>`<tr><td>${m.date}</td><td><a href="missioni/${escape(m.id)}.html">${escape(m.name)}</a></td><td>${escape(m.id)}</td><td>${escape(m.family)}</td></tr>`).join('');
fs.writeFileSync(path.join(directory,'elenco.html'),`<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Elenco delle missioni | Archivio SpaceX</title><link rel="stylesheet" href="archivio.css"></head><body><header><a class="brand" href="../../index.html">Rivoluzione Spaziale</a><nav aria-label="Navigazione"><a href="index.html">Ricerca nell’archivio</a><a href="metodo.html">Metodo e fonti</a></nav></header><main><p class="eyebrow">Indice statico delle schede</p><h1>Tutte le missioni documentate</h1><p>${missions.length} schede (${aggregate(missions).launches} decolli e ${missions.length-aggregate(missions).launches} evento pre-lancio); importazione ${raw.imported}. Comprende registro principale e prove integrate Starship, senza doppio conteggio del volo 14.</p><div class="table-scroll"><table><thead><tr><th>Data</th><th>Missione</th><th>ID</th><th>Famiglia</th></tr></thead><tbody>${staticLinks}</tbody></table></div></main><footer>Archivio SpaceX</footer></body></html>\n`);
console.log(JSON.stringify({ missions: missions.length, principal: main.length, additional: additional.length, vehicles: data.vehicles.length, corrections: corrections.length, checks }, null, 2));
