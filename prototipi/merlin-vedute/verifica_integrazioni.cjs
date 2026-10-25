/* Conservazione rispetto a 0346576, tabelle, collegamenti e comandi del ciclo. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {execFileSync}=require('node:child_process'),{pathToFileURL}=require('node:url');
const {chromium}=require('C:/Users/Utente/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..'),qa=path.join(__dirname,'qa'),base='03465767b81b5e08a7942aefd0678ae2ab20f425';
const git=(...args)=>execFileSync('git',args,{cwd:root,maxBuffer:30*1024*1024});
const baseline=git('show',`${base}:atlante/spacex/merlin.html`).toString('utf8');
const article=JSON.parse(fs.readFileSync(path.join(root,'atlante/spacex/merlin-articolo.json'),'utf8'));
const additions=JSON.parse(fs.readFileSync(path.join(root,'atlante/spacex/merlin-integrazioni.json'),'utf8'));
fs.mkdirSync(qa,{recursive:true});
for(const f of ['atlante/spacex/merlin-articolo.json','atlante/spacex/schede.json','atlante/spacex/merlin-vedute.css','atlante/spacex/atlante.css','atlante/spacex/atlante.js','assets/raptor-full-flow/flow.css','assets/raptor-full-flow/flow.js']){
 assert.equal(fs.readFileSync(path.join(root,f),'utf8').replaceAll('\r\n','\n'),git('show',`${base}:${f}`).toString('utf8').replaceAll('\r\n','\n'),f);
}
assert.deepEqual(git('diff','--name-only',base,'--','*.html').toString().trim().split(/\r?\n/),['atlante/spacex/merlin.html']);
assert.ok(Math.abs(108300/190000*100-57)<1e-10);
assert.ok(Math.abs(119000/170000*100-70)<1e-10);
assert.ok(Math.abs(140679/220500*100-63.8)<.000001);
assert.ok(Math.abs(81000/210000*100-38.6)<.05);
assert.equal(Math.round(92500*4.4482216152605/1000),411);
assert.equal(Math.round(1859*6894.757293168/1e6*100)/100,12.82);
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Users/Utente/AppData/Local/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-win64/chrome-headless-shell.exe'});
 const results=[];
 try{
  for(const width of [1440,768,390,320])for(const javaScriptEnabled of [true,false]){
   const ctx=await browser.newContext({viewport:{width,height:1000},javaScriptEnabled,reducedMotion:'reduce'});
   const p=await ctx.newPage(),errors=[],failed=[];
   p.on('pageerror',e=>errors.push(e.message));p.on('requestfailed',r=>failed.push(r.url()));
   await p.goto(pathToFileURL(path.join(root,'atlante/spacex/merlin.html')).href);
   const report=await p.evaluate(({baseline,article,additions})=>{
    const previous=new DOMParser().parseFromString(baseline,'text/html'),problems=[];
    const same=(selector)=>{
     const a=[...previous.querySelectorAll(selector)],b=[...document.querySelectorAll(selector)];
     if(a.length!==b.length||a.some((e,i)=>e.outerHTML!==b[i].outerHTML))problems.push(`conservazione ${selector}`);
    };
    for(const s of article.sections){same(`#${s.id}>h2`);same(`#${s.id}>p`);}
    for(const selector of ['#vedute-merlin','.photo','header','footer','script','.sources ol>li:nth-child(-n+14)'])same(selector);
    // Il JS aggiunge lo zoom e aggiorna stato/pulsante; si confronta il contenuto statico separatamente.
    const oldFlow=previous.querySelector('#schema-animato'),flow=document.querySelector('#schema-animato');
    if(oldFlow.querySelector('figcaption').outerHTML!==flow.querySelector('figcaption').outerHTML)problems.push('didascalia ciclo');
    if(oldFlow.querySelector('img').getAttribute('src')!==flow.querySelector('img').getAttribute('src'))problems.push('poster ciclo');
    const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
    if(new Set(ids).size!==ids.length)problems.push('ID duplicati');
    for(const a of document.querySelectorAll('a[href^="#"]'))if(!document.getElementById(a.hash.slice(1)))problems.push(`ancora ${a.hash}`);
    if(document.querySelectorAll('.merlin-addition').length!==additions.blocks.length)problems.push('integrazioni mancanti');
    const tables=[...document.querySelectorAll('.merlin-table')].map(t=>({rows:t.tBodies[0].rows.length,columns:t.tHead.rows[0].cells.length,scroll:t.parentElement.scrollWidth>t.parentElement.clientWidth}));
    for(const t of document.querySelectorAll('.merlin-table')){
     if(!t.caption||!t.parentElement.hasAttribute('tabindex'))problems.push('accessibilità tabella');
     for(const th of t.querySelectorAll('th'))if(!th.scope)problems.push('intestazione senza scope');
    }
    const broken=[...document.querySelectorAll('a[href],img[src],link[href],script[src]')].map(e=>e.getAttribute('href')||e.getAttribute('src')).filter(v=>v&&!/^(https?:|#|mailto:)/.test(v));
    return {problems,tables,local:broken,pageWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth,images:[...previous.querySelectorAll('img[src]')].map(e=>e.getAttribute('src'))};
   },{baseline,article,additions});
   assert.deepEqual(report.problems,[]);
   assert.ok(report.scrollWidth<=report.pageWidth+1,`${width}: overflow`);
   assert.deepEqual(report.tables.map(x=>[x.rows,x.columns]),[[13,4],[9,7],[4,6]]);
   if(width<=390)assert.ok(report.tables.every(x=>x.scroll));
   for(const href of report.local){
    const file=decodeURIComponent(href.split(/[?#]/)[0]);assert.ok(fs.existsSync(path.resolve(root,'atlante/spacex',file)),href);
   }
   for(const src of report.images){
    const file=decodeURIComponent(src.split('?')[0]),abs=path.resolve(root,'atlante/spacex',file),rel=path.relative(root,abs).replaceAll('\\','/');
    if(rel.endsWith('.svg'))assert.equal(fs.readFileSync(abs,'utf8').replaceAll('\r\n','\n'),git('show',`${base}:${rel}`).toString('utf8').replaceAll('\r\n','\n'),rel);
    else assert.ok(fs.readFileSync(abs).equals(git('show',`${base}:${rel}`)),rel);
   }
   for(const img of await p.locator('img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate(e=>e.decode());}
   if(javaScriptEnabled){
    const f=p.locator('#schema-animato');await f.scrollIntoViewIfNeeded();
    await f.locator('[data-flow-toggle]').click();await p.waitForFunction(()=>document.querySelector('#schema-animato').dataset.playing==='true');
    await f.locator('img').evaluate(e=>e.decode());
    await f.locator('[data-flow-toggle]').click();await p.waitForFunction(()=>document.querySelector('#schema-animato').dataset.playing==='false');
    await f.getByRole('button',{name:'Ingrandisci lo schema nella pagina',exact:true}).click();assert.equal(await f.locator('[aria-pressed]').getAttribute('aria-pressed'),'true');
    await f.getByRole('button',{name:'Ingrandisci lo schema nella pagina',exact:true}).click();
    for(const id of ['parametri-merlin','versioni-merlin','cronologia-anomalie-merlin','glossario-merlin']){
     const section=p.locator('#'+id);await section.screenshot({path:path.join(qa,`${id}-${width}.png`)});
    }
    for(const region of await p.locator('.merlin-table-scroll').all()){
     await region.focus();await region.evaluate(e=>{e.scrollLeft=0;});await p.keyboard.press('ArrowRight');
     if(width<=390){await p.waitForFunction(()=>document.activeElement.scrollLeft>0);}
    }
   }
   assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
   results.push({width,javaScriptEnabled,tables:3,chaptersPreserved:13,originalReferencesPreserved:14,noOverflow:true,noErrors:true});
   console.log('OK integrazioni',width,javaScriptEnabled?'JS':'senza JS');await ctx.close();
  }
  fs.writeFileSync(path.join(qa,'integrazioni.json'),JSON.stringify({baseline:base,results},null,2)+'\n');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
