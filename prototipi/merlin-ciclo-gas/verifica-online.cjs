/* Confronto byte per byte con l'ultimo commit pubblicato. Nessuna scrittura remota. */
const {execFileSync}=require('node:child_process');
const {createHash}=require('node:crypto');
const files=['atlante/spacex/merlin.html','atlante/spacex/schemi/merlin.svg','assets/merlin-ciclo-gas/merlin-ciclo-gas.gif','assets/merlin-ciclo-gas/merlin-ciclo-gas.svg'];
const sha=execFileSync('git',['rev-parse','HEAD']).toString().trim();
const hash=b=>createHash('sha256').update(b).digest('hex');
const base='https://paolozamparutti197-cpu.github.io/rivoluzione-spaziale/';
(async()=>{
 let failures=0;
 await Promise.all(files.map(async file=>{
  const expected=execFileSync('git',['show',`HEAD:${file}`],{maxBuffer:16*1024*1024});
  const response=await fetch(base+file+'?verifica='+sha,{headers:{'Cache-Control':'no-cache'},signal:AbortSignal.timeout(30000)});
  const received=Buffer.from(await response.arrayBuffer());
  const match=response.ok&&hash(received)===hash(expected);
  console.log(JSON.stringify({file,status:response.status,bytes:received.length,mime:response.headers.get('content-type'),match}));
  if(!match)failures++;
 }));
 if(failures)throw Error(`${failures} file online non corrispondono al commit ${sha}`);
 console.log(`PUBBLICAZIONE VERIFICATA: ${files.length} file identici al commit ${sha}`);
})().catch(e=>{console.error(e);process.exit(1);});
