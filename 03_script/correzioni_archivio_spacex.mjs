// Revisione del sito separata dai gestori Python e dai registri Excel.
export function applyWikipediaCorrections(missions, review) {
  const byId = new Map(missions.map(m => [m.id, m]));
  const allowed = /^(date|name|pad|padId|orbit|launch\.outcome|flights\.[012]\.(serial|ordinal|recovery\.(attempt|landed|physical|mode|notes)))$/;
  const decisions = [];
  for (const c of review.checks) {
    const m=byId.get(c.id);
    if (!m) throw Error(`Missione verificata assente: ${c.id}`);
    for (const [field,expected] of Object.entries(c.expectedOriginal)) {
      const value=field.split('.').reduce((o,k)=>o?.[k],m);
      const patch=review.patches.find(p=>p.missionId===c.id&&p.field===field);
      if (JSON.stringify(value)!==JSON.stringify(expected) && (!patch || JSON.stringify(value)!==JSON.stringify(patch.after)))
        throw Error(`Fonte cambiata: ${c.id} ${field}; verifica Wikipedia da aggiornare.`);
    }
  }
  // Prima controlla tutte le precondizioni: nessun aggiornamento parziale.
  for (const p of review.patches) {
    if (!allowed.test(p.field)) throw Error(`Campo correzione non ammesso: ${p.field}`);
    const m = byId.get(p.missionId);
    if (!m) throw Error(`Correzione senza missione: ${p.missionId}`);
    const parts = p.field.split('.');
    const obj = parts.slice(0,-1).reduce((o,k) => o?.[k],m);
    const value = obj?.[parts.at(-1)];
    if (JSON.stringify(value) !== JSON.stringify(p.before) && JSON.stringify(value) !== JSON.stringify(p.after))
      throw Error(`Fonte cambiata: ${p.missionId} ${p.field}; rivedere correzioni-wikipedia.json prima di pubblicare.`);
  }
  for (const p of review.patches) {
    const m = byId.get(p.missionId), parts = p.field.split('.');
    const obj = parts.slice(0,-1).reduce((o,k) => o[k],m);
    obj[parts.at(-1)] = p.after;
    decisions.push({id:`${m.id}:wikipedia:${p.field}`,missionId:m.id,date:review.date,kind:'correzione documentata',
      text:`${p.field}: ${JSON.stringify(p.before)} → ${JSON.stringify(p.after)}.${p.reason ? ` ${p.reason}` : ''}`,
      sources:[m.source,p.source,...(p.references || [])],action:'Correzione applicata al sito. Valore originale conservato nella fotografia Excel e nella revisione.',before:p.before,after:p.after,field:p.field});
    m.references = [...new Set([...m.references,p.source,...(p.references || [])])];
  }
  for (const c of review.checks) {
    const m=byId.get(c.id);
    if (!m || m.family==='Starship' && m.originalPhase!=='Operativo') throw Error(`Perimetro verifica Wikipedia invalido: ${c.id}`);
    const {expectedOriginal,...verified}=c;
    m.wikipedia = {...verified,checked:review.date};
    m.references=[...new Set([...m.references,c.source])];
  }
  return decisions;
}
