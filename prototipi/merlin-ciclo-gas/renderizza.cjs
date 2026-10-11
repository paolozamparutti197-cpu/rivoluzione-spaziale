/* Render locale SVG -> PNG ad alta risoluzione e fotogrammi per la GIF. */
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require('C:/Users/Utente/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=__dirname;
const frameDir=path.join(root,'fotogrammi');
fs.mkdirSync(frameDir,{recursive:true});
const config=JSON.parse(fs.readFileSync(path.join(root,'flussi.json'),'utf8'));
const mode=process.argv.includes('--solo-anteprima')?'preview':'all';
(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:'C:/Users/Utente/AppData/Local/ms-playwright/chromium_headless_shell-1223/chrome-headless-shell-win64/chrome-headless-shell.exe'});
  const page=await browser.newPage({viewport:{width:1800,height:1400},deviceScaleFactor:1});
  await page.goto(pathToFileURL(path.join(root,'anteprima.html')).href);
  await page.evaluate(()=>{window.pauseDiagram();window.setDiagramTime(0);});
  const bounds=await page.evaluate(()=>[...document.querySelectorAll('svg text')].map(n=>{const b=n.getBBox();return {text:n.textContent,x:b.x,y:b.y,w:b.width,h:b.height};}).filter(b=>b.x<0||b.y<0||b.x+b.w>1800||b.y+b.h>1300));
  if(bounds.length)throw new Error(`Testi fuori tavola: ${JSON.stringify(bounds)}`);
  await page.locator('main svg').screenshot({path:path.join(root,'controllo-impaginazione.png')});
  // Rasterizzazione mediante SVG come immagine: non dipende dalla larghezza della toolbar.
  async function raster(t,scale=1) {
    return await page.evaluate(async({t,scale})=>{
      window.setDiagramTime(t);
      const svg=document.querySelector('main svg');
      const xml=new XMLSerializer().serializeToString(svg);
      const blob=new Blob([xml],{type:'image/svg+xml;charset=utf-8'});
      const url=URL.createObjectURL(blob);
      const img=new Image();
      await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=reject;img.src=url;});
      const canvas=document.createElement('canvas');canvas.width=1800*scale;canvas.height=1300*scale;
      canvas.getContext('2d').drawImage(img,0,0,canvas.width,canvas.height);URL.revokeObjectURL(url);
      return {png:canvas.toDataURL('image/png').split(',')[1],svg:xml};
    },{t,scale});
  }
  const poster=await raster(.72,2);
  fs.writeFileSync(path.join(root,'merlin-ciclo-gas.png'),Buffer.from(poster.png,'base64'));
  fs.writeFileSync(path.join(root,'merlin-ciclo-gas.svg'),poster.svg.replace(/[ \t]+$/gm,''),'utf8');
  fs.writeFileSync(path.join(root,'verifica-percorsi.json'),JSON.stringify(await page.evaluate(()=>window.diagramAudit()),null,2),'utf8');
  if(mode==='all') {
    const total=150;
    for(let i=0;i<total;i++) {
      const {png}=await raster(i*6/total);
      fs.writeFileSync(path.join(frameDir,`${String(i).padStart(3,'0')}.png`),Buffer.from(png,'base64'));
      if(i%25===0)console.log(`Fotogrammi: ${i}/${total}`);
    }
    console.log(`Fotogrammi: ${total}/${total}`);
    const a=await raster(0), b=await raster(6);
    if(a.png!==b.png)throw new Error('Il ciclo non torna esattamente allo stesso fotogramma.');
    console.log('Ciclo continuo verificato: t=0 e t=6 producono pixel identici.');
  }
  await browser.close();console.log('Rendering verificato: testi entro la tavola, SVG e PNG prodotti.');
})().catch(e=>{console.error(e);process.exit(1);});
