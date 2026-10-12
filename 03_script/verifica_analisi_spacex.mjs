// Controlli manuali, offline per default. Non corregge dati o attiva automazioni.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';
import {costModel,replacementModel} from '../analisi/spacex/modelli.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),folder=path.join(root,'analisi/spacex');
const manifest=JSON.parse(fs.readFileSync(path.join(folder,'manifest.json')));
const result=JSON.parse(fs.readFileSync(path.join(folder,'dati/calcoli.json')));
const config=JSON.parse(fs.readFileSync(path.join(folder,'dossier.json')));
const registry=JSON.parse(fs.readFileSync(path.join(folder,'registro-correzioni.json')));
const original=fs.readFileSync(path.join(root,'archivio/spacex/dati.json'));
const snapshot=fs.readFileSync(path.join(folder,'dati/snapshot-archivio.json'));
assert.ok(original.equals(snapshot),'Il registro e la copia di calcolo divergono: rigenerare.');
assert.equal(createHash('sha256').update(snapshot).digest('hex'),result.sourceSha256);
assert.equal(manifest.sourceSha256,result.sourceSha256);
assert.equal(manifest.automationsActivated,false);
execFileSync(process.execPath,[path.join(root,'03_script/genera_analisi_spacex.mjs'),'--check'],{cwd:root,stdio:'inherit'});
const data=JSON.parse(original);
// Uno snapshot storico resta valido se un workbook successivo cambia (anche solo
// metadati Excel). Segnalare la differenza, non sovrascrivere o fingere coerenza.
const workbookFingerprints=data.sources.filter(s=>s.file.endsWith('.xlsx')).map(s=>{
 const current=createHash('sha256').update(fs.readFileSync(path.join(root,s.file))).digest('hex');
 return {file:s.file,recorded:s.sha256,current,matches:current===s.sha256};
});
if(process.argv.includes('--require-current-workbooks'))assert.ok(workbookFingerprints.every(s=>s.matches),'Workbook attuali e snapshot divergono; verificare la pipeline, senza sovrascritture automatiche.');
assert.equal(new Set(registry.entries.map(r=>r.id)).size,registry.entries.length);
for(const r of result.annual){
 assert.equal(r.starlink+r.other,r.launches);
 assert.equal(r.missionIds.length,r.launches);
 assert.ok(r.reflights<=r.boosterFlights);
 const selected=data.missions.filter(m=>r.missionIds.includes(m.id));
 assert.ok(selected.every(m=>m.family!=='Starship'&&m.launch.id));
 assert.equal(r.boosterFlights,selected.reduce((n,m)=>n+m.flights.length,0));
}
assert.ok(result.sameCutoff[0].cutoff.slice(5)===result.sameCutoff[1].cutoff.slice(5),'Confronto infrannuale non omogeneo.');
assert.equal(result.intervals.filter(i=>i.to.startsWith('2025')).length,result.availability2025.consecutivePairs);
assert.equal(result.initialCost.average,costModel().average);
assert.equal(costModel({flights:1,refurb:99}).average,135);
assert.equal(costModel({stage:0,refurb:0,other:0}).ratio,null);
assert.ok(costModel({refurb:200,flights:10}).average>costModel({refurb:200,flights:1}).average);
for(const invalid of [NaN,Infinity,-1,0])assert.throws(()=>replacementModel({lifetime:invalid}));
assert.throws(()=>costModel({flights:1.5}));assert.throws(()=>replacementModel({satellites:12.5}));
let links=0,anchors=0;
for(const item of manifest.outputs.filter(f=>f.endsWith('.html'))){
 const file=path.join(folder,item),html=fs.readFileSync(file,'utf8');
 assert.ok(!/\{\{[\w]+\}\}/.test(html),`Segnaposto: ${item}`);
 assert.ok(html.includes('<html lang="it">')&&html.includes('name="viewport"'),item);
 for(const image of html.matchAll(/<img\b([^>]+)>/g))assert.ok(/\balt="[^"]+"/.test(image[1]),`Alt mancante ${item}`);
 for(const m of html.matchAll(/\b(?:href|src)="([^"]+)"/g)){
  const url=m[1].replaceAll('&amp;','&');if(/^(https?:|data:|mailto:)/.test(url))continue;
  const [filepart,hash]=url.split('#'),target=path.resolve(path.dirname(file),decodeURIComponent(filepart.split('?')[0]||path.basename(file)));
  assert.ok(target===root||target.startsWith(root+path.sep),`Link fuori workspace: ${url}`);
  assert.ok(fs.existsSync(target),`Link locale mancante: ${item} -> ${url}`);links++;
  if(hash&&target.endsWith('.html')){const targetHtml=fs.readFileSync(target,'utf8');assert.ok(targetHtml.includes(`id="${decodeURIComponent(hash)}"`)||targetHtml.includes(`name="${decodeURIComponent(hash)}"`),`Ancora assente: ${item} -> ${url}`);anchors++;}
 }
}
const asOfIndex=process.argv.indexOf('--as-of'),asOf=asOfIndex>=0?process.argv[asOfIndex+1]:new Date().toISOString().slice(0,10);
assert.ok(/^\d{4}-\d{2}-\d{2}$/.test(asOf));
const due=config.articles.filter(a=>a.reviewDue<asOf).map(a=>({id:a.id,due:a.reviewDue}));
const newDataNeedsReview=data.imported>config.editorialReview;
const external=[];
if(process.argv.includes('--links')){
 const sources=JSON.parse(fs.readFileSync(path.join(folder,'fonti.json')));
 for(const s of Object.values(sources).filter(s=>s.url.startsWith('https:'))){
  try{const r=await fetch(s.url,{method:'HEAD',redirect:'follow',signal:AbortSignal.timeout(15000)});external.push({url:s.url,status:r.status,accessible:r.ok});}
  catch(e){external.push({url:s.url,error:e.message,accessible:false});}
 }
 // I blocchi ai robot non sono interpretati come confutazioni del documento.
}
const report={asOf,articles:3,charts:5,links,anchors,modelsChecked:true,snapshotIdentical:true,workbookFingerprints,reviewDue:due,newDataNeedsReview,external,automationsActivated:false};
if(process.argv.includes('--report')){
 const target=path.join(root,'99_temporanei/verifica_analisi_spacex.json');fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,JSON.stringify(report,null,2)+'\n');
}
console.log(JSON.stringify(report,null,2));
if((due.length||newDataNeedsReview)&&process.argv.includes('--strict-review'))process.exitCode=1;
