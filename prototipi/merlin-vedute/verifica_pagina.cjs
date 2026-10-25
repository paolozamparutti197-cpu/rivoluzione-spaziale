/* Controlli della galleria: immagini, accessibilità di base e layout responsivo. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const {chromium}=require('C:/Users/Utente/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..'),qa=path.join(__dirname,'qa');
fs.mkdirSync(qa,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Users/Utente/AppData/Local/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-win64/chrome-headless-shell.exe'});
 const checks=[];
 try{
  for(const width of [1440,390])for(const javaScriptEnabled of [true,false]){
   const ctx=await browser.newContext({viewport:{width,height:1000},javaScriptEnabled,reducedMotion:'reduce'});
   const p=await ctx.newPage(),errors=[],failed=[];
   p.on('pageerror',e=>errors.push(e.message));p.on('requestfailed',r=>failed.push(r.url()));
   await p.goto(pathToFileURL(path.join(root,'atlante/spacex/merlin.html')).href);
   const gallery=p.locator('#vedute-merlin');
   assert.equal(await gallery.locator('figure').count(),4);
   for(const img of await gallery.locator('img').all()){
    await img.scrollIntoViewIfNeeded();
    await img.evaluate(i=>i.decode());
    const info=await img.evaluate(i=>({src:i.currentSrc,w:i.naturalWidth,h:i.naturalHeight,alt:i.alt}));
    // naturalWidth è corretto per la densità quando il browser usa srcset.
    assert.ok(info.w>300&&info.h>0&&info.src.endsWith('.webp'),JSON.stringify(info));assert.ok(info.alt.length>70);
   }
   const dimensions=await p.evaluate(()=>({width:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth}));
   assert.ok(dimensions.scrollWidth<=dimensions.width+1,JSON.stringify(dimensions));
   assert.ok((await gallery.innerText()).includes('non fotografie'));
   assert.equal(await p.locator('#schema-animato').count(),1);
   for(const a of await gallery.locator('a').all()){
    const href=await a.getAttribute('href');
    if(href.startsWith('../../assets/'))assert.ok(fs.existsSync(path.resolve(root,'atlante/spacex',href)),href);
   }
   assert.deepEqual(errors,[]);assert.deepEqual(failed,[]);
   if(javaScriptEnabled){
    await gallery.screenshot({path:path.join(qa,`merlin-vedute-${width}.png`)});
   }
   checks.push({width,javaScriptEnabled,images:4,noOverflow:true,noErrors:true});
   console.log('OK',width,javaScriptEnabled?'JS':'senza JS');await ctx.close();
  }
  fs.writeFileSync(path.join(qa,'verifica.json'),JSON.stringify({checks},null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
