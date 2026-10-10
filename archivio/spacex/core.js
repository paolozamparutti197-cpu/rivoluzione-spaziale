// Un solo aggregatore per interfaccia, esportazione e controlli.
export function filterMissions(missions, f = {}) {
  const q = (f.q || '').toLocaleLowerCase('it').trim();
  return missions.filter(m => {
    const event = f.event || 'launch';
    if (event === 'launch' && !m.launch.id || event === 'prelaunch' && m.launch.id) return false;
    const scope = f.scope || 'operational';
    if (scope === 'operational' && m.scope === 'test') return false;
    if (scope === 'falcon' && m.family === 'Starship') return false;
    if (scope === 'tests' && m.scope !== 'test') return false;
    if (['mixed','starship'].includes(scope) && !(m.family === 'Starship' && m.originalPhase === 'Operativo')) return false;
    if (f.family && m.family !== f.family || f.pad && m.pad !== f.pad || f.outcome && (m.launch.outcome || 'unknown') !== f.outcome || f.class && m.class !== f.class) return false;
    if (f.from && m.date < f.from || f.to && m.date > f.to) return false;
    if (f.payload && (m.payload.outcome || 'unknown') !== f.payload) return false;
    if (f.recovery === 'yes' && !m.flights.some(v => v.role !== 'Ship' && v.recovery.landed === 1)) return false;
    if (f.recovery === 'no' && !m.flights.some(v => v.role !== 'Ship' && v.recovery.landed === 0 && v.recovery.attempt === 1)) return false;
    if (f.recovery === 'unknown' && !m.flights.some(v => v.role !== 'Ship' && v.recovery.attempt == null)) return false;
    if (f.reuse === 'yes' && !m.flights.some(v => v.ordinal > 1)) return false;
    if (f.reuse === 'unknown' && !m.flights.some(v => v.ordinal == null)) return false;
    if (f.gaps === 'yes' && !m.issues.length) return false;
    if (f.booster && !m.flights.some(v => (v.serial || '').toLowerCase().includes(f.booster.toLowerCase()))) return false;
    return !q || [m.id, m.name, m.family, m.launcher, m.notes, ...m.flights.map(v => v.serial)].join(' ').toLocaleLowerCase('it').includes(q);
  });
}
export function aggregate(missions) {
  const flights = missions.flatMap(m => m.flights);
  const boosters = flights.filter(v => v.role !== 'Ship');
  const recoveryDecided = boosters.filter(v => v.recovery.attempt === 1 && [0, 1].includes(v.recovery.landed));
  const launchDecided = missions.filter(m => m.launch.id && ['successo', 'parziale', 'fallito'].includes(m.launch.outcome));
  const cargoDecided = missions.filter(m => ['successo', 'parziale', 'fallito'].includes(m.payload.outcome));
  return {
    missions: missions.length,
    launches: new Set(missions.map(m => m.launch.id).filter(Boolean)).size,
    launchDecided: launchDecided.length,
    launchSuccess: launchDecided.filter(m => m.launch.outcome === 'successo').length,
    payloadDecided: cargoDecided.length,
    payloadSuccess: cargoDecided.filter(m => m.payload.outcome === 'successo').length,
    boosterFlights: boosters.length,
    knownBoosters: new Set(boosters.map(v => v.serial).filter(Boolean)).size,
    missingSerial: boosters.filter(v => !v.serial).length,
    reflights: boosters.filter(v => v.ordinal > 1).length,
    ordinalUnknown: boosters.filter(v => v.ordinal == null).length,
    recoveryAttempts: boosters.filter(v => v.recovery.attempt === 1).length,
    recoveryDecided: recoveryDecided.length,
    landingSuccess: boosters.filter(v => v.recovery.landed === 1).length,
    landingRateNumerator: recoveryDecided.filter(v => v.recovery.landed === 1).length,
    recoveryUnknown: boosters.filter(v => v.recovery.attempt == null).length,
    physicalRecoveries: flights.filter(v => v.recovery.physical === 1).length,
    physicalKnown: flights.filter(v => [0, 1].includes(v.recovery.physical)).length,
    gaps: missions.filter(m => m.issues.length).length,
  };
}
export function annualSeries(missions) {
  const years = [...new Set(missions.filter(m=>m.launch.id).map(m => m.date.slice(0, 4)))].sort();
  return years.map(year => ({ year, ...aggregate(missions.filter(m => m.date.startsWith(year))) }));
}
export function compareYears(missions, a, b, sameCutoff, cutoff) {
  const monthDay = cutoff.slice(5);
  return [a, b].map(year => {
    const [month,day] = monthDay.split('-').map(Number);
    const boundedDay = Math.min(day,new Date(Date.UTC(year,month,0)).getUTCDate());
    const bounded = `${String(month).padStart(2,'0')}-${String(boundedDay).padStart(2,'0')}`;
    const selected = missions.filter(m => m.date.startsWith(String(year)) && (!sameCutoff || m.date.slice(5) <= bounded));
    return { year, cutoff: sameCutoff ? `${year}-${bounded}` : `${year}-12-31`, ...aggregate(selected) };
  });
}
export const csvCell = value => '"' + String(value ?? '').replace(/^[=+@-]/, "'$&").replaceAll('"', '""') + '"';
export function csv(rows) {
  if (!rows.length) return '';
  const keys = Object.keys(rows[0]);
  return '\uFEFF' + [keys.map(csvCell).join(';'), ...rows.map(r => keys.map(k => csvCell(r[k])).join(';'))].join('\r\n');
}
export function missionRows(missions) {
  return missions.map(m => ({ id_missione: m.id, id_lancio: m.launch.id, tipo_evento: m.launch.id ? 'decollo' : 'pre-lancio', data: m.date, missione: m.name, famiglia: m.family,
    perimetro: m.scope, fase_originale: m.originalPhase, lanciatore: m.launcher, pad: m.pad, classe: m.class,
    esito_lancio: m.launch.outcome, esito_payload: m.payload.outcome, numero_payload: m.payload.count,
    booster: m.flights.filter(v => v.role !== 'Ship').map(v => v.serial || 'non documentato').join(', '),
    fonte: m.source, note: m.notes, anomalie: m.issues.join(' / ') }));
}
export function flightRows(missions) {
  return missions.flatMap(m => m.flights.map(v => ({ id_volo: v.id, id_missione: m.id, data: m.date, ruolo: v.role,
    matricola: v.serial, progressivo: v.ordinal, tentativo_recupero: v.recovery.attempt,
    atterraggio_cattura_riuscito: v.recovery.landed, recupero_fisico: v.recovery.physical,
    landing_originale: v.recovery.mode, fonte: v.source, nota_rientro: v.recovery.notes })));
}
export function validate(data) {
  const errors = [], ids = new Set(), launches = new Set(), flightIds = new Set();
  const fail = message => errors.push(message);
  for (const m of data.missions) {
    if (!m.id || ids.has(m.id)) fail(`Missione duplicata/mancante: ${m.id}`);
    ids.add(m.id);
    if (!['Falcon 1','Falcon 9','Falcon Heavy','Starship'].includes(m.family)) fail(`Famiglia non riconosciuta: ${m.id}`);
    if (!['falcon','test','operational'].includes(m.scope)) fail(`Perimetro non riconosciuto: ${m.id}`);
    if (m.family==='Starship' && m.scope==='operational' && m.originalPhase!=='Operativo') fail(`Starship operativa senza fase Operativo: ${m.id}`);
    if (m.launch.id && launches.has(m.launch.id)) fail(`Lancio duplicato: ${m.launch.id}`);
    if (m.launch.id) launches.add(m.launch.id);
    if (!m.launch.id && (m.flights.length || m.launch.outcome)) fail(`Evento pre-lancio con voli o esito di lancio: ${m.id}`);
    if (m.launch.missionId !== m.id || m.attempt.missionId !== m.id || m.launch.attemptId !== m.attempt.id) fail(`Relazione missione/tentativo/lancio: ${m.id}`);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(m.date) || Number.isNaN(Date.parse(m.date)) || new Date(m.date).toISOString().slice(0, 10) !== m.date || m.date > data.imported) fail(`Data non valida/futura: ${m.id}`);
    if (!['successo', 'parziale', 'fallito', null].includes(m.launch.outcome)) fail(`Esito non ammesso: ${m.id}`);
    if (!['successo', 'parziale', 'fallito', null].includes(m.payload.outcome)) fail(`Esito carico non ammesso: ${m.id}`);
    if (m.payload.count != null && (!Number.isInteger(m.payload.count) || m.payload.count < 0)) fail(`Numero carichi: ${m.id}`);
    if (m.family === 'Falcon Heavy' && (m.flights.length !== 3 || new Set(m.flights.map(v => v.role)).size !== 3)) fail(`Falcon Heavy senza tre ruoli: ${m.id}`);
    const serials = m.flights.map(v => v.serial).filter(Boolean);
    if (new Set(serials).size !== serials.length) fail(`Veicolo ripetuto nello stesso lancio: ${m.id}`);
    for (const v of m.flights) {
      if (flightIds.has(v.id)) fail(`Volo veicolo duplicato: ${v.id}`);
      flightIds.add(v.id);
      if (v.launchId !== m.launch.id) fail(`Volo senza lancio: ${v.id}`);
      if (v.ordinal != null && (!Number.isInteger(v.ordinal) || v.ordinal < 1)) fail(`Progressivo invalido: ${v.id}`);
      for (const k of ['attempt', 'landed', 'physical']) if (![null, 0, 1].includes(v.recovery[k])) fail(`Flag invalido ${k}: ${v.id}`);
      if (v.recovery.landed === 1 && v.recovery.attempt === 0) fail(`Recupero riuscito senza tentativo: ${v.id}`);
    }
  }
  const tests = data.missions.filter(m => m.family === 'Starship');
  const programs = tests.map(m => m.programFlight);
  if (new Set(programs).size !== programs.length) fail('Volo Starship duplicato fra registri');
  return errors;
}
