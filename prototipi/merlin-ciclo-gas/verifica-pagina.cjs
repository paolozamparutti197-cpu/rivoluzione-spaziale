/* QA del lettore e regressione Raptor: sola lettura delle pagine, nessun deploy. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const {chromium}=require('C:/Users/Utente/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..');
async function loaded(page){await page.waitForFunction(()=>{const i=document.querySelector('[data-raptor-flow] img');return i?.complete&&i.naturalWidth===1800;},null,{timeout:20000});}
async function state(page){return page.evaluate(()=>{const f=document.querySelector('[data-raptor-flow]'),i=f.querySelector('img'),v=f.querySelector('.raptor-flow-view');return {src:i.getAttribute('src'),playing:f.dataset.playing,imageWidth:i.getBoundingClientRect().width,viewWidth:v.clientWidth,viewScrollWidth:v.scrollWidth,documentWidth:document.documentElement.clientWidth,documentScrollWidth:document.documentElement.scrollWidth};});}
function noOverflow(s){assert.ok(s.documentScrollWidth<=s.documentWidth+1,JSON.stringify(s));}
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Users/Utente/AppData/Local/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-win64/chrome-headless-shell.exe'});
 const rows=[];
 try{
  for(const id of ['merlin','raptor'])for(const width of [1440,390])for(const mode of ['normal','reduced','nojs']){
   const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:mode==='reduced'?'reduce':'no-preference',javaScriptEnabled:mode!=='nojs'});
   const page=await context.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto(pathToFileURL(path.join(root,`atlante/spacex/${id}.html`)).href+'#schema-animato');
   await page.locator('[data-raptor-flow]').scrollIntoViewIfNeeded();
   await loaded(page);
   if(mode!=='nojs')await page.waitForFunction(expected=>document.querySelector('[data-raptor-flow]').dataset.playing===expected,mode==='normal'?'true':'false');
   const initial=await state(page);noOverflow(initial);
   assert.ok(initial.src.includes(mode==='normal'?'.gif':'.svg'),JSON.stringify(initial));
   if(width===390)assert.ok(initial.viewScrollWidth>initial.viewWidth);
   const caption=await page.locator('[data-raptor-flow] figcaption').innerText();
   assert.ok(caption.includes('original')&&caption.includes('costruttiv'));
   if(id==='merlin')assert.ok(caption.includes('albero comune')&&!caption.includes('monografia Starship'));
   if(mode!=='nojs'){
    const toggle=page.locator('[data-flow-toggle]');
    if(mode==='normal'){await toggle.click();await loaded(page);assert.equal((await state(page)).playing,'false');}
    await toggle.click();await loaded(page);assert.equal((await state(page)).playing,'true');
    await page.locator('button').filter({hasText:/^Ingrandisci$/}).click();
    const zoom=await state(page);noOverflow(zoom);assert.equal(zoom.imageWidth,1800);
    await page.locator('button').filter({hasText:/^Adatta alla pagina$/}).click();noOverflow(await state(page));
    await toggle.click();await loaded(page);
    if(mode==='normal')await page.locator('[data-raptor-flow]').screenshot({path:path.join(__dirname,`controllo-pagina-${id}-${width}.png`)});
   }else assert.equal(await page.locator('[data-flow-toggle]').isVisible(),false);
   assert.equal(errors.length,0,JSON.stringify(errors));
   rows.push({id,width,mode,initial,caption,errors});
   console.log(`OK ${id} ${width} ${mode}`);await context.close();
  }
  const poster=fs.readFileSync(path.join(root,'assets/merlin-ciclo-gas/merlin-ciclo-gas.svg'));
  assert.deepEqual(fs.readFileSync(path.join(root,'atlante/spacex/schemi/merlin.svg')),poster);
  fs.writeFileSync(path.join(__dirname,'verifica-pagina.json'),JSON.stringify({tests:rows.length,rows,alias_identical:true},null,2));
  console.log(`Verificati ${rows.length} casi e alias SVG.`);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
