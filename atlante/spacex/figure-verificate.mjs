// Figure specifiche: niente sagome anatomiche o collegamenti assegnati in automatico.
import fs from 'node:fs';
import path from 'node:path';
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const nasaLicense='https://www.nasa.gov/nasa-brand-center/images-and-media/';
const photoConfigs={
 'falcon-9':{path:'../../documenti per sito/assets_fondazione/falcon9-2014/crs3-pad-gambe.jpg',size:[3000,2000],crop:[1230,70,390,1700],author:'SpaceX',license:'CC0 1.0',licenseUrl:'https://creativecommons.org/publicdomain/zero/1.0/',source:'https://commons.wikimedia.org/wiki/File:Falcon_9_with_CRS-3_Dragon_on_SLC-40_pad_(16166732954).jpg',date:'17 aprile 2014 · Falcon 9 v1.1 / CRS-3',labels:[['Dragon', 'L',170,1480,210],['Secondo stadio','R',290,1500,425],['Primo stadio','L',470,1500,1000],['Gamba ripiegata','R',580,1500,1570]],notes:['Configurazione storica v1.1, non Block 5.','Merlin Vacuum e nove Merlin del primo stadio: non visibili.']},
 'dragon-cargo-1':{photo:'dragon1-approach',size:[1920,1275],crop:[490,150,1030,1080],date:'25 maggio 2012 · Dragon C2+',labels:[['Interfaccia di berthing','L',160,800,300],['Capsula','L',340,770,600],['Trunk','L',550,800,1010],['Pannello solare','R',450,1240,855]],notes:['Prima generazione: pannelli solari dispiegabili.','Scudo termico sotto la capsula: nascosto in questa vista.']},
 'crew-dragon':{path:'assets/crew-dragon-demo2-2020.jpg',size:[1920,1280],crop:[220,15,1120,1240],author:'NASA / Chris Cassidy',license:'Materiale NASA per uso informativo',licenseUrl:nasaLicense,source:'https://www.nasa.gov/image-article/spacex-crew-dragon-approaches-international-space-station-4/',date:'31 maggio 2020 · Endeavour / Demo-2',labels:[['Cono anteriore aperto','L',150,725,215],['Interfaccia di attracco','R',350,770,690],['Capsula','L',570,535,950]],notes:['Il cono aperto espone la zona di attracco.','Trunk, scudo termico e SuperDraco non identificabili in questa vista.']},
 'cargo-dragon-2':{path:'assets/cargo-dragon-crs26-2022.jpg',size:[5568,3712],crop:[2420,1440,760,820],author:'NASA / ISS Expedition 68',license:'Materiale NASA per uso informativo',licenseUrl:nasaLicense,source:'https://www.nasa.gov/image-article/spacex-dragon-cargo-craft-approaches-space-station/',date:'27 novembre 2022 · Cargo Dragon / CRS-26',labels:[['Cono anteriore aperto','L',150,2710,1640],['Interfaccia di attracco','R',350,2790,1950],['Capsula cargo','L',560,2630,2070]],notes:['Cargo Dragon 2: attracco autonomo alla ISS.','Trunk e carichi interni non visibili; niente SuperDraco nella variante cargo.']},
 'super-heavy':{photo:'starship/ift5-approach.jpg',size:[1920,2044],crop:[900,55,260,650],date:'13 ottobre 2024 · Super Heavy / Flight 5',labels:[['Griglia aerodinamica','L',150,975,118],['Corpo del booster','R',340,1020,360],['Zona di propulsione','L',590,1020,590]],notes:['Booster in ritorno: Ship si è già separata.','I singoli Raptor e i serbatoi interni non sono distinguibili.']},
 'ship':{photo:'starship/sn15.jpg',size:[1280,1864],crop:[0,0,1280,1864],date:'2021 · prototipo SN15',labels:[['Ogiva','R',150,950,220],['Flap anteriore','L',380,595,980],['Superficie in acciaio','R',550,1090,930]],notes:['Dettaglio storico di SN15: non la configurazione orbitale attuale.','Serbatoi, motori e scudo orbitale non vengono indicati come visibili.']}
};
const text=(x,y,s,cls='')=>`<text x="${x}" y="${y}" ${cls?`class="${cls}"`:''}>${esc(s)}</text>`;
function frame(title,desc,body,height=820){return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 ${height}" role="img" aria-labelledby="title desc"><title id="title">${esc(title)}</title><desc id="desc">${esc(desc)}</desc><defs><marker id="flow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto-start-reverse"><path d="M0 0L8 4L0 8Z" fill="#67d5df"/></marker><marker id="heat" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#efbd78"/></marker></defs><style>text{font-family:Arial,sans-serif;fill:#f4f6f3;font-size:24px}.heading{font-size:30px;font-weight:bold}.small{font-size:20px;fill:#cad9df}.tiny{font-size:17px;fill:#cad9df}.box{fill:#1c3544;stroke:#547b8c;stroke-width:2}.flow{fill:none;stroke:#67d5df;stroke-width:3;marker-end:url(#flow)}.pressure{fill:none;stroke:#efbd78;stroke-width:3;stroke-dasharray:8 6;marker-end:url(#heat)}</style><rect width="1000" height="${height}" fill="#11232f"/>${text(30,48,title,'heading')}${body}</svg>`;}
function node(x,y,w,lines,h=86){return `<rect class="box" x="${x}" y="${y}" width="${w}" height="${h}" rx="5"/>${lines.map((s,i)=>text(x+16,y+30+i*28,s,i?'small':'')).join('')}`;}
const flow=(d,pressure=false)=>`<path class="${pressure?'pressure':'flow'}" d="${d}"/>`;
function photoFigure(c,cfg,data,root){
 const p=cfg.photo?{...data.photos[cfg.photo],...cfg}:cfg;
 const file=path.resolve(root,decodeURIComponent(p.path)),jpeg=fs.readFileSync(file).toString('base64');
 const [iw,ih]=p.size,[cx,cy,cw,ch]=p.crop,px=255,py=98,pw=490,ph=590,scale=Math.min(pw/cw,ph/ch),ox=px+(pw-cw*scale)/2,oy=py+(ph-ch*scale)/2;
 const note=`${p.author}; ${p.license}. Inquadratura di dettaglio e annotazioni vettoriali; JPEG non ritoccato. ${p.date}.`+(p.license.includes('BY-SA')?' La figura annotata conserva la stessa licenza della fotografia.':'');
 c.diagram.labels=p.labels.map(l=>l[0]);
 c.diagram.title='Fotografia annotata: componenti visibili';
 c.diagram.description=p.labels.map(l=>l[0]).join('; ')+'. '+p.notes.join(' ');
 c.diagram.note=note+' '+p.notes.join(' ');
 c.diagram.credit={author:p.author,source:p.source,license:p.license,licenseUrl:p.licenseUrl};
 let body=text(30,80,p.date,'small')+`<svg x="${px}" y="${py}" width="${pw}" height="${ph}" viewBox="${cx} ${cy} ${cw} ${ch}" preserveAspectRatio="xMidYMid meet"><image width="${iw}" height="${ih}" href="data:image/jpeg;base64,${jpeg}"/></svg>`;
 for(const [label,side,y,tx,ty] of p.labels){
  const x=side==='L'?15:765,sx=side==='L'?235:765,sy=y+10,xx=ox+(tx-cx)*scale,yy=oy+(ty-cy)*scale;
  body+=`<path d="M${sx} ${sy} L${xx} ${yy}" stroke="#fff" stroke-width="7"/><path d="M${sx} ${sy} L${xx} ${yy}" stroke="#006775" stroke-width="3"/><circle cx="${xx}" cy="${yy}" r="5" fill="#006775" stroke="#fff" stroke-width="2"/><rect x="${x-5}" y="${y-16}" width="225" height="62" rx="4" fill="#11232f"/>`;
  const words=label.split(' '),lines=[''];for(const w of words){if((lines.at(-1)+' '+w).trim().length>19)lines.push(w);else lines[lines.length-1]=(lines.at(-1)+' '+w).trim();}
  body+=lines.map((l,i)=>text(x,y+8+i*23,l,'small')).join('');
 }
 body+=p.notes.map((s,i)=>text(25,738+i*29,s,'small')).join('')+text(25,802,`${p.author} · annotazioni editoriali · fonte e condizioni nella scheda`,'tiny');
 return frame(c.title+' · dettagli riconoscibili',c.diagram.description,`<metadata>${esc(note+' Fonte: '+p.source+' Licenza: '+p.licenseUrl)}</metadata>`+body);
}
function falcon1(c){
 c.diagram.title='Architettura a due stadi';c.diagram.description='Carenatura sopra il secondo stadio; Kestrel nel secondo stadio; interstadio; primo stadio con un Merlin. Disegno funzionale, non una sezione costruttiva.';c.diagram.note='Ricostruzione editoriale dell’architettura, verificata sulle fonti Falcon 1 della scheda. I motori interni sono indicati nel disegno, non su una fotografia. Dimensioni e impianti omessi.';
 const b=`<path d="M430 178 Q465 65 500 178Z" fill="#dce5e8" stroke="#7d9aaa" stroke-width="2"/><rect x="430" y="178" width="70" height="138" fill="#dce5e8"/><rect x="430" y="316" width="70" height="66" fill="#273a48"/><rect x="430" y="382" width="70" height="275" fill="#dce5e8"/><path d="M450 303L443 326L487 326L480 303Z M450 650L443 681L487 681L480 650Z" fill="#efbd78" stroke="#11232f" stroke-width="2"/>`;
 const labels=[['Carenatura',135,143,430,145],['Secondo stadio',660,220,500,220],['Kestrel',135,310,453,312],['Interstadio',660,356,500,353],['Primo stadio',135,508,430,505],['Un Merlin',660,675,480,662]];
 return frame('Falcon 1 · due stadi, due motori',c.diagram.description,b+labels.map(([s,x,y,tx,ty])=>text(x,y,s)+`<path d="M${x<500?345:640} ${y-7}L${tx} ${ty}" stroke="#67d5df" stroke-width="2"/><circle cx="${tx}" cy="${ty}" r="4" fill="#67d5df"/>`).join('')+text(30,760,'Posizioni funzionali: non in scala, non un disegno di officina.','small')+text(30,797,'Kestrel: alimentazione pressurizzata. Merlin: ciclo a generatore di gas.','small'));
}
function engine(c){
 c.diagram.title='Schema del principio di alimentazione';c.diagram.note='Schema funzionale editoriale, non planimetria del motore: frecce continue per i flussi principali, tratteggiate per la pressurizzazione. Valvole ausiliarie, raffreddamento e sistemi di avviamento omessi. Verifica nelle fonti della scheda.';
 let b='',desc='';
 if(['kestrel','draco','superdraco'].includes(c.id)){
  const hyper=c.id!=='kestrel';desc=hyper?'Gas di pressurizzazione verso entrambi i serbatoi; ossidante e MMH attraverso valvole separate fino alla camera. Nessuna turbopompa.':'Gas di pressurizzazione verso entrambi i serbatoi; LOX e RP-1 attraversano valvole separate fino alla camera. Nessuna turbopompa.';
  b=node(340,110,320,['Gas di pressurizzazione'])+node(45,265,320,[hyper?'Ossidante ipergolico':'Ossigeno liquido',hyper?'Serbatoio NTO':'Serbatoio LOX'])+node(635,265,320,[hyper?'Monometilidrazina':'Cherosene RP-1',hyper?'Serbatoio MMH':'Serbatoio RP-1'])+node(45,450,320,['Valvola ossidante'])+node(635,450,320,['Valvola combustibile'])+node(330,630,340,['Camera di combustione','Ugello e gas di scarico'])+flow('M400 196 V225 H205 V265',true)+flow('M600 196 V225 H795 V265',true)+flow('M205 351 V450')+flow('M795 351 V450')+flow('M205 536 V673 H330')+flow('M795 536 V673 H670')+text(30,775,hyper?'Accensione al contatto dei propellenti · nessuna turbopompa':'Alimentazione pressurizzata · accensione non ipergolica','small');
 }else if(c.id==='merlin'){
  c.diagram.note='Schema editoriale del ciclo a generatore di gas: azzurro per i flussi, tratteggio oro per il collegamento meccanico turbina-pompe. Una parte dei propellenti passa nel generatore; il gas della turbina non rientra nella camera principale. Raffreddamento, valvole e avviamento omessi.';
  desc='LOX e RP-1 alimentano le pompe e la camera principale. Una parte dei propellenti alimenta il generatore di gas; il gas aziona la turbina e non ritorna nella camera principale. L’albero collega turbina e pompe.';
  b=node(40,110,300,['Ossigeno liquido','Serbatoio LOX'])+node(660,110,300,['Cherosene','Serbatoio RP-1'])+node(40,280,300,['Pompa ossidante'])+node(660,280,300,['Pompa combustibile'])+node(350,390,300,['Generatore di gas','Solo parte dei flussi'])+node(350,530,300,['Turbina','Aziona le pompe'])+node(40,660,300,['Camera principale','Ugello propulsivo'])+node(660,660,300,['Scarico del gas','Fuori dalla camera']);
  b+=flow('M190 196 V280')+flow('M810 196 V280')+flow('M190 366 V660')+flow('M810 366 V620 H275 V660')+flow('M190 400 H350 V430')+flow('M810 400 H650 V430')+flow('M500 476 V530')+flow('M650 573 H810 V660')+`<path d="M350 573H310V322H340 M650 573H690V370H960V322" fill="none" stroke="#efbd78" stroke-width="3" stroke-dasharray="8 6"/>`+text(340,245,'Tratteggio: collegamento meccanico','tiny')+text(30,790,'Ciclo aperto a generatore di gas · scarico separato dalla camera principale','small');
 }else{
  c.diagram.note='Schema editoriale full-flow: pompe, due precombustori, due turbine e camera principale. Sono mostrate anche le alimentazioni incrociate necessarie ai precombustori. Non è un disegno costruttivo Raptor: alberi meccanici, raffreddamento, pressurizzazione e valvole omessi.';
  desc='Due pompe e due precombustori, uno ricco di ossigeno e uno ricco di metano. Entrambi i flussi attraversano le turbine e raggiungono la camera principale; piccole alimentazioni incrociate consentono la combustione nei precombustori.';
  b=node(35,105,360,['Ossigeno liquido','Pompa ossidante'])+node(605,105,360,['Metano liquido','Pompa combustibile'])+node(35,315,360,['Precombustore','Ricco di ossigeno'])+node(605,315,360,['Precombustore','Ricco di metano'])+node(35,505,360,['Turbina lato ossidante'])+node(605,505,360,['Turbina lato combustibile'])+node(330,665,340,['Camera principale','Combustione finale']);
  b+=flow('M215 191 V315')+flow('M785 191 V315')+flow('M215 401 V505')+flow('M785 401 V505')+flow('M215 591 V708 H330')+flow('M785 591 V708 H670')+flow('M215 230 H470 V285 H675 V315')+flow('M785 245 H530 V270 H325 V315')+text(365,215,'Alimentazioni incrociate','tiny')+text(30,797,'Full-flow: entrambi i flussi arrivano alla camera · albero pompe omesso','small');
 }
 c.diagram.description=desc;return frame(c.title+' · circuito funzionale',desc,b);
}
function network(c){
 c.diagram.title='Percorso dei dati: nodi e collegamenti';c.diagram.note='Topologia funzionale editoriale, non una mappa di copertura né una disposizione orbitale. Le linee descrivono collegamenti dati bidirezionali; i percorsi laser sono opzionali e non appartengono a tutte le generazioni.';
 let b='',desc='';
 if(c.id==='direct-to-cell'){
  desc='Telefono compatibile comunica via radio con un satellite Direct to Cell; la rete spaziale si collega all’infrastruttura terrestre e al core dell’operatore mobile. Non è richiesto un terminale domestico Starlink.';
  b=node(55,125,365,['Telefono compatibile','Accesso radio mobile'])+node(580,125,365,['Satellite Direct to Cell','Accesso dallo spazio'])+node(580,365,365,['Rete spaziale / gateway','Trasporto verso terra'])+node(55,365,365,['Core operatore mobile','Autenticazione e servizi'])+node(55,605,365,['Destinazione','Internet o rete telefonica']);
  b+=bi('M420 168H580')+bi('M762 211V365')+bi('M580 408H420')+bi('M237 451V605')+text(30,765,'Il partner mobile non è un satellite: qui è un nodo terrestre.','small')+text(30,795,'Frequenze, compatibilità e servizi dipendono dalle autorizzazioni locali.','small');
 }else if(c.id==='starlink-terminali'){
  desc='Dispositivi locali e router comunicano con l’antenna Starlink, che si collega via radio ai satelliti disponibili. Il satellite si collega alla rete terrestre, direttamente o attraverso altri satelliti.';
  b=node(45,110,390,['Dispositivi e rete locale'])+node(565,110,390,['Router'])+node(565,330,390,['Antenna Starlink','Inseguimento elettronico'])+node(45,330,390,['Satellite disponibile','Accesso radio'])+node(45,580,390,['Rete verso destinazione','Gateway e/o laser']);
  b+=bi('M435 153H565')+bi('M760 196V330')+bi('M565 373H435')+bi('M240 416V580')+text(30,745,'Antenna e router sono apparati diversi; il passaggio di satellite è dinamico.','small')+text(30,780,'Ostacoli, alimentazione e configurazione locale influiscono sul servizio.','small');
 }else{
  desc='Terminale utente, satellite e gateway sono nodi diversi. Il traffico può raggiungere il gateway direttamente oppure attraverso satelliti collegati da laser; poi attraversa la rete terrestre verso la destinazione.';
  b=node(30,120,300,['Satellite A','Accesso dell’utente'])+node(670,120,300,['Satellite B','Collegamento al gateway'])+node(30,410,300,['Terminale utente','Collegamento radio'])+node(670,410,300,['Gateway terrestre','Collegamento radio'])+node(355,645,290,['Rete terrestre','Destinazione dei dati']);
  b+=bi('M330 163H670',true)+text(360,135,'Laser, se disponibili','tiny')+bi('M180 206V410')+bi('M820 206V410')+bi('M820 496V688H645')+`<path d="M330 183L680 410" fill="none" stroke="#a5bbc6" stroke-width="2" stroke-dasharray="8 6" marker-start="url(#flow)" marker-end="url(#flow)"/>`+text(420,370,'Alternativa: radio diretta','tiny')+text(30,780,c.id==='starlink-generazioni'?'Le generazioni coesistono; la dotazione laser dipende dall’hardware.':'Il percorso laser non sostituisce il collegamento radio con l’utente.','small');
 }
 c.diagram.description=desc;return frame(c.title+' · rete funzionale',desc,b);
}
function bi(d,dashed=false){return `<path class="flow" d="${d}" marker-start="url(#flow)" ${dashed?'stroke-dasharray="10 6"':''}/>`;}
function special(c){
 if(c.id==='starmind'){
  c.diagram.title='Energia, dati e calore: tre percorsi distinti';c.diagram.description='Energia solare e accumulo alimentano il calcolo. Il calcolo scambia dati con la rete ottica e cede calore al circuito termico e ai radiatori. Non è una singola catena sequenziale.';c.diagram.note='Schema funzionale editoriale del concetto di calcolo orbitale, non planimetria di AI1. Energia, dati e calore sono percorsi differenti; geometria, prestazioni e dettagli proprietari non rappresentati.';
  return frame('Calcolo orbitale · tre circuiti',c.diagram.description,node(30,140,320,['Generazione solare'])+node(650,140,320,['Distribuzione / accumulo'])+node(350,350,300,['Processori e memoria'])+node(30,570,320,['Rete ottica','Scambio di dati'])+node(650,570,320,['Circuito termico','Radiatori verso lo spazio'])+flow('M350 183H650')+flow('M810 226V390H650')+bi('M350 393H190V570')+flow('M650 393H810V570',true)+text(30,760,'Azzurro: energia e dati (percorsi distinti). Oro: calore.','small')+text(30,795,'Il radiatore smaltisce calore: non è una fase successiva della rete dati.','small'));
 }
 if(c.id==='recupero-starship'){
  c.diagram.title='Due stadi, due percorsi di ritorno';c.diagram.description='Dopo la separazione, Super Heavy ritorna lungo il proprio profilo mentre Ship prosegue la missione e affronta un rientro separato. Ispezione e qualifica al rivolo sono valutate per ciascun veicolo.';c.diagram.note='Schema di missione editoriale: i percorsi dei due stadi sono paralleli, non una sequenza unica. Recupero, cattura e rivolo dipendono dall’esito e dagli obiettivi del singolo volo.';
  return frame('Recupero Starship · percorsi separati',c.diagram.description,node(320,100,360,['Separazione degli stadi'])+node(35,300,400,['Super Heavy','Profilo di ritorno del booster'])+node(565,300,400,['Ship','Prosegue la propria missione'])+node(35,500,400,['Ritorno del booster','Cattura / esito del test'])+node(565,500,400,['Rientro della nave','Zona prevista / esito del test'])+node(35,690,400,['Ispezione del booster','Eventuale qualifica al rivolo'])+node(565,690,400,['Ispezione della nave','Eventuale qualifica al rivolo'])+flow('M400 186V240H235V300')+flow('M600 186V240H765V300')+flow('M235 386V500')+flow('M765 386V500')+flow('M235 586V690')+flow('M765 586V690'),840);
 }
 return null;
}
export function verifiedFigure(c,data,root){
 let svg;
 if(photoConfigs[c.id])svg=photoFigure(c,photoConfigs[c.id],data,root);
 else if(c.id==='falcon-1')svg=falcon1(c);
 else if(c.diagram.type==='engine'&&['merlin','kestrel','draco','superdraco','raptor'].includes(c.id))svg=engine(c);
 else if(c.diagram.type==='network'&&['starlink-generazioni','starlink-laser','starlink-terminali','direct-to-cell','stazioni-terra'].includes(c.id))svg=network(c);
 else svg=special(c);
 if(svg!==null){c.diagram.reviewed='2026-10-11';if(!photoConfigs[c.id])delete c.diagram.labels;}
 return svg;
}
export function figureMethod(data){
 return '<h2>Figure tecniche e fotografie annotate</h2><p>Le 32 figure sono state riesaminate l’11 ottobre 2026. Falcon Heavy, Falcon 9, Dragon cargo di prima generazione, Crew Dragon, Cargo Dragon 2, Super Heavy e Ship usano fotografie autentiche con annotazioni vettoriali. Le inquadrature di dettaglio sono dichiarate; i JPEG non sono ritoccati. Le linee terminano soltanto su elementi riconoscibili. Motori, serbatoi e carichi nascosti non vengono indicati come visibili. Le altre figure sono schemi funzionali editoriali: non sezioni costruttive, planimetrie o mappe di copertura. Sono distinti flussi, pressurizzazione, collegamenti meccanici, percorsi dei dati e rientri separati dei due stadi. La figura Falcon 1 rappresenta esplicitamente un’architettura disegnata, non una fotografia. Il generatore conserva le figure specifiche e non ripristina le precedenti sagome generiche.</p><div class="credits-list">'+data.cards.filter(c=>c.diagram.credit).map(c=>{const p=c.diagram.credit;return `<article><h3>${esc(c.title)}: figura annotata</h3><p>${esc(p.author)} · ${esc(p.license)}. <a href="${esc(p.source)}">Fonte della fotografia</a> · <a href="${esc(p.licenseUrl)}">Condizioni di riutilizzo</a>.</p></article>`;}).join('')+'</div>';
}
