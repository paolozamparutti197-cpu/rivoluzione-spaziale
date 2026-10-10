import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {aggregate,filterMissions,validate,compareYears,annualSeries,csv} from '../archivio/spacex/core.js';
import {applyWikipediaCorrections} from './correzioni_archivio_spacex.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const read=name=>JSON.parse(fs.readFileSync(path.join(root,'archivio/spacex',name),'utf8'));
const data=read('dati.json'),snapshot=read('fonti-snapshot.json'),report=read('riconciliazione.json');
assert.deepEqual(validate(data),[]);
const fh=filterMissions(data.missions,{family:'Falcon Heavy'}),fsum=aggregate(fh);
assert.equal(fsum.launches,fh.length);
assert.equal(fsum.boosterFlights,fh.length*3);
assert.equal(new Set(fh.flatMap(m=>m.flights.map(v=>v.id))).size,fsum.boosterFlights);
assert.equal(data.missions.filter(m=>m.family==='Starship'&&m.programFlight===14).length,1);
assert.equal(data.missions.filter(m=>m.family==='Starship').length,snapshot.tests.length);
assert.equal(aggregate(data.missions).launches,data.coverage.principal+data.coverage.starshipTests-data.coverage.starshipOverlap-data.coverage.prelaunchEvents);
const amos=data.missions.find(m=>m.id==='SX-0034');
assert.equal(amos.launch.id,null);
assert.equal(aggregate([amos]).launches,0);
assert.equal(aggregate([amos]).boosterFlights,0);
assert.equal(filterMissions(data.missions,{event:'prelaunch',scope:'all'}).length,1);
assert.equal(aggregate(filterMissions(data.missions,{scope:'tests'})).launchDecided,0);
assert.equal(aggregate(filterMissions(data.missions,{scope:'tests'})).launchSuccess,0);
const sourceMain=snapshot.launches.filter(r=>r.tipo_record==='Lancio principale');
assert.equal(sourceMain.length,data.coverage.principal);
const review=read('correzioni-wikipedia.json');
const originalSuccess=sourceMain.filter(r=>r.stato==='successo').length;
assert.equal(aggregate(data.missions).launchSuccess,originalSuccess-1); // CRS-1 complessivamente parziale.
assert.equal(data.missions.find(m=>m.id==='SX-0009').launch.outcome,'parziale');
assert.equal(filterMissions(data.missions).length,data.coverage.principalLaunches);
assert.ok(filterMissions(data.missions).every(m=>m.family!=='Starship'||m.originalPhase==='Operativo'));
assert.equal(filterMissions(data.missions,{scope:'tests'}).length,data.coverage.starshipTests-data.coverage.starshipOverlap);
assert.equal(filterMissions(data.missions,{scope:'starship'}).length,sourceMain.filter(m=>m.famiglia_lanciatore==='Starship'&&m.fase_programma==='Operativo').length);
assert.equal(new Set(review.checks.map(c=>c.id)).size,review.summary.matchedLaunches);
for (const c of review.checks) {
  const m=data.missions.find(m=>m.id===c.id);
  assert.equal(m.date,c.dateUTC);
  for (const [field,before] of Object.entries(c.expectedOriginal)) {
    const p=review.patches.find(p=>p.missionId===c.id&&p.field===field);
    assert.deepEqual(field.split('.').reduce((o,k)=>o[k],m),p?p.after:before);
  }
}
for (const p of review.patches) {
  const m=data.missions.find(m=>m.id===p.missionId);
  assert.deepEqual(p.field.split('.').reduce((o,k)=>o[k],m),p.after);
}
const incompatible=structuredClone(data.missions);
incompatible.find(m=>m.id==='SX-0714').name='Fonte cambiata';
assert.throws(()=>applyWikipediaCorrections(incompatible,review),/Fonte cambiata/);
assert.deepEqual(applyWikipediaCorrections(structuredClone(data.missions),review).length,review.patches.length);
assert.equal(report.workbookFlags.landingSuccess,report.principalStatistics.landingSuccess);
assert.ok(report.principalStatistics.reflights>=snapshot.launches.filter(r=>typeof r.voli==='number'&&r.voli>1).length);
const missingPayload=data.missions.find(m=>m.launch.outcome==='successo'&&!m.payload.outcome);
assert.ok(missingPayload);
assert.equal(aggregate([missingPayload]).payloadDecided,0);
const missingSerial=data.missions.find(m=>m.flights.some(v=>!v.serial));
if (missingSerial) assert.ok(aggregate([missingSerial]).missingSerial>0);
assert.equal(data.missions.find(m=>m.id==='SX-0381').flights[0].serial,'B1075');
assert.equal(data.missions.find(m=>m.id==='SX-0381').flights[0].ordinal,12);
assert.equal(data.missions.find(m=>m.id==='SX-0299').flights[0].serial,'B1084');
assert.equal(data.missions.find(m=>m.id==='SX-0299').flights[0].ordinal,1);
assert.equal(data.missions.find(m=>m.id==='SX-0396').flights.filter(v=>v.recovery.landed===1).length,0);
const flight13=data.missions.find(m=>m.id==='IFT-13');
assert.equal(flight13.flights.find(v=>v.role==='Ship').recovery.physical,1);
assert.equal(data.missions.find(m=>m.id==='SX-0710').flights.reduce((n,v)=>n+(v.recovery.physical||0),0),0);
assert.equal(aggregate(filterMissions(data.missions,{family:'Falcon Heavy',from:'2023-01-01',to:'2023-12-31'})).launches,5);
const subset=filterMissions(data.missions,{scope:'all',q:'Starlink',from:'2026-01-01',to:'2026-10-10'});
assert.ok(subset.every(m=>m.name.toLowerCase().includes('starlink')||m.notes.toLowerCase().includes('starlink')));
assert.ok(subset.every(m=>m.date>='2026-01-01'&&m.date<='2026-10-10'));
assert.equal(annualSeries(subset).reduce((n,y)=>n+y.launches,0),aggregate(subset).launches);
const [a,b]=compareYears(data.missions,2025,2026,true,data.coverageEnd);
assert.ok(a.cutoff.endsWith('-10-10')&&b.cutoff.endsWith('-10-10'));
assert.equal(a.launches,aggregate(data.missions.filter(m=>m.date>='2025-01-01'&&m.date<='2025-10-10')).launches);
assert.equal(compareYears(data.missions,2025,2024,true,'2024-02-29')[0].cutoff,'2025-02-28');
assert.equal(report.latestComparison.matches,true);
const none=aggregate([]);assert.equal(none.launches,0);assert.equal(none.recoveryDecided,0);
assert.ok(csv([{nome:'=HYPERLINK("test")',nota:'a;b\nc'}]).includes("'=HYPERLINK"));
function rejects(change,pattern) {const bad=structuredClone(data);change(bad);assert.ok(validate(bad).some(x=>pattern.test(x)));}
rejects(d=>d.missions.push(d.missions[0]),/duplicat/);
rejects(d=>d.missions.find(m=>m.family==='Falcon Heavy').flights.pop(),/tre ruoli/);
rejects(d=>{const r=d.missions.find(m=>m.flights.length).flights[0].recovery;r.attempt=0;r.landed=1;},/senza tentativo/);
rejects(d=>d.missions[0].date='2026-02-30',/Data/);
rejects(d=>d.missions.find(m=>m.flights.length).flights[0].recovery.physical=2,/Flag invalido/);
rejects(d=>d.missions.find(m=>m.flights.length).flights[0].ordinal=0,/Progressivo/);
rejects(d=>d.missions.find(m=>m.programFlight===14).programFlight=13,/Starship duplicato/);
console.log(`Controlli superati: ${data.missions.length} schede, ${aggregate(data.missions).launches} decolli, ${fh.length} Falcon Heavy (${fsum.boosterFlights} voli booster).`);
