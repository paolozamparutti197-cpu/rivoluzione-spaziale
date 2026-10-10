const $ = id => document.getElementById(id);
const escape = x => String(x ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
try {
  const responses = await Promise.all(['riconciliazione.json','dati.json','registro-correzioni.json'].map(p=>fetch(p)));
  if (responses.some(r=>!r.ok)) throw Error('Rapporto non disponibile');
  const [report,data,records] = await Promise.all(responses.map(r=>r.json()));
  $('date').textContent = `Importazione ${data.imported}; ultima data coperta ${data.coverageEnd}.`;
  $('reconciliation').innerHTML = `<p><b>${data.coverage.principal}</b> record principali (di cui ${data.coverage.principalLaunches} decolli e l’evento pre-lancio Amos-6) e <b>${data.coverage.additional}</b> righe aggiuntive di booster. <b>${data.coverage.starshipTests}</b> voli integrati Starship, di cui uno già nel registro principale. Totale riconciliato: <b>${report.statistics.launches}</b> decolli e <b>${data.missions.length-report.statistics.launches}</b> evento pre-lancio.</p><div class="table-scroll"><table><thead><tr><th>Voce</th><th>Nuova vista riconciliata</th><th>Sito storico</th><th>Confronto</th></tr></thead><tbody>${report.legacyComparison.map(r=>`<tr><td>${escape(r.label)}</td><td>${r.workbook}</td><td>${r.site ?? 'non disponibile'}</td><td>${r.matches ? 'Coincide' : 'Diverge'}</td></tr>`).join('')}</tbody></table></div><p>Flag dell’Excel: ${report.workbookFlags.recoveryAttempts} tentativi di recupero; ${report.workbookFlags.landingSuccess} atterraggi riusciti; ${report.workbookFlags.reflightFlags} riutilizzi segnati. Reflight con progressivo documentato nei soli lanci principali e relativi booster: ${report.principalStatistics?.reflights ?? 'vedere ricerca'}.</p><p>${report.schemaErrors.length ? 'Controlli strutturali con errori.' : 'Controlli strutturali superati.'} Le anomalie delle fonti restano nel registro qui sotto.</p><p>Ultima missione del riepilogo: ${report.latestComparison.site ? escape(report.latestComparison.site.name) : 'non disponibile'}. Confronto con l’Excel: ${report.latestComparison.matches ? 'coincide' : 'diverge'}.</p>`;
  $('hashes').innerHTML = data.sources.map(s=>`<p>${escape(s.file)}<br>${escape(s.sha256)}</p>`).join('');
  let limit = 40;
  function renderRecords() {
    const q = $('audit-search').value.toLocaleLowerCase('it');
    const filtered = records.filter(r=>[r.missionId,r.text,r.kind,r.status].join(' ').toLocaleLowerCase('it').includes(q));
    $('audit-count').textContent = `${filtered.length} voci corrispondenti; ${Math.min(limit,filtered.length)} visualizzate.`;
    $('audit').innerHTML = filtered.slice(0,limit).map(r=>`<article class="record"><p><a href="missioni/${encodeURIComponent(r.missionId)}.html">${escape(r.missionId)}</a> · ${escape(r.kind)} · ${escape(r.date)}${r.status === 'risolta' ? ' · risolta nel registro corrente' : ''}</p><p>${escape(r.text)}</p><p class="source">${r.sources.map(escape).join(' / ')}</p><p class="source">${escape(r.action)}</p></article>`).join('');
    $('audit-more').hidden = limit >= filtered.length;
  }
  $('audit-search').addEventListener('input',()=>{limit=40;renderRecords();});
  $('audit-more').addEventListener('click',()=>{limit+=40;renderRecords();});
  renderRecords();
} catch(error) { $('reconciliation').textContent = 'Rapporto non disponibile. Consulta i file JSON collegati oppure riprova.';console.error(error); }
