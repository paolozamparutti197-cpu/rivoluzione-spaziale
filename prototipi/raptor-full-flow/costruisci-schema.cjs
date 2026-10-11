/* Tavola originale. Genera solo artefatti locali, senza operazioni Git o rete. */
const fs = require('node:fs');
const path = require('node:path');
const out = __dirname;
const W = 1800, H = 1300;
const C = {bg:'#0a111d', panel:'#101c2c', edge:'#31465b', ink:'#f1f6fb', muted:'#adbdcf', fuel:'#51dfba', lox:'#69b9ff', fr:'#ffbb68', ox:'#c3a4ff', fire:'#ffe19a', metal:'#bfccd8'};
const esc = s => String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const text = (x,y,s,size=22,fill=C.ink,extra='') => `<text x="${x}" y="${y}" font-size="${size}" fill="${fill}" ${extra}>${esc(s)}</text>`;
const lines = (x,y,ss,size=22,fill=C.ink,extra='',gap=size*1.3) => ss.map((s,i)=>text(x,y+i*gap,s,size,fill,extra)).join('');
const line = (d,stroke=C.muted,width=1.5,extra='') => `<path d="${d}" fill="none" stroke="${stroke}" stroke-width="${width}" ${extra}/>`;
const dot = (x,y,color) => `<circle cx="${x}" cy="${y}" r="6" fill="${color}" stroke="${C.bg}" stroke-width="2"/>`;
const flowSpecs = [];
function flow(id,d,color,width=19,kind='liquid',period=6,spacing=88) {
  flowSpecs.push({id,d,color,width,kind,period,spacing});
  if(width<=3) return `<path id="${id}" d="${d}" fill="none" stroke="${color}" stroke-width="1" stroke-opacity=".2" data-flow="true"/>`;
  return `<g class="conduit" data-stream="${kind}">
    ${line(d,C.bg,width+11,'stroke-linecap="round" stroke-linejoin="round"')}
    ${line(d,C.edge,width+5,'stroke-linecap="round" stroke-linejoin="round"')}
    ${line(d,color,width,'stroke-opacity=".27" stroke-linecap="round" stroke-linejoin="round"')}
    ${kind==='gas'?line(d,color,2,'stroke-opacity=".45" stroke-dasharray="2 8" stroke-linecap="round"'):''}
    <path id="${id}" d="${d}" fill="none" stroke="transparent" data-flow="true"/>
  </g>`;
}
const leader = d => line(d,'#8398af',1.5,'stroke-linecap="round"');
function rotor(cx,cy,r,unit,type) {
  let blades = '';
  const n=type==='pump'?7:12;
  for(let i=0;i<n;i++) {
    const blade=type==='pump'?`M5 -${r-4} C${r*.65} -${r*.83} ${r*.56} -${r*.23} 8 -7 L2 -12 C${r*.18} -${r*.37} ${r*.28} -${r*.6} 0 -${r-4} Z`:`M-4 -${r-3} L7 -${r-4} L11 -${r*.47} L1 -${r*.36} Z`;
    blades+=`<path d="${blade}" transform="rotate(${i*360/n})" fill="url(#bladeMetal)" stroke="#9cb0c4" stroke-width=".7"/>`;
  }
  return `<g data-rotor="${unit}" data-cx="${cx}" data-cy="${cy}" transform="translate(${cx} ${cy})">${blades}<circle r="9" fill="#d8e5ee" stroke="#647b90" stroke-width="2"/><circle r="3" fill="#233549"/></g>`;
}
function pump(cx,color,unit,name,mirror=false) {
  const cy=282;
  return `<g aria-label="${name}">
    <circle cx="${cx}" cy="${cy}" r="57" fill="url(#bodyMetal)" stroke="#afc3d6" stroke-width="2"/>
    <circle cx="${cx}" cy="${cy}" r="47" fill="${color}" fill-opacity=".16" stroke="${color}" stroke-opacity=".7" stroke-width="2"/>
    <circle cx="${cx}" cy="${cy}" r="36" fill="#101b2a" stroke="#829bb0" stroke-width="1.3"/>
    ${rotor(cx,cy,33,unit,'pump')}
    <path d="M${cx-10} 223H${cx+10}V244H${cx-10}Z" fill="${color}" fill-opacity=".28" stroke="#b9d0de" stroke-width="1.4"/>
    <path d="M${mirror?cx+44:cx-63} 272H${mirror?cx+63:cx-44}V292H${mirror?cx+44:cx-63}Z" fill="${color}" fill-opacity=".28" stroke="#b9d0de" stroke-width="1.4"/>
    ${[45,135,225,315].map(a=>`<circle cx="${cx+52*Math.cos(a*Math.PI/180)}" cy="${cy+52*Math.sin(a*Math.PI/180)}" r="2.5" fill="#b8c6d5"/>`).join('')}
  </g>`;
}
function turbine(cx,color,unit,mirror=false) {
  const cy=508;
  return `<g aria-label="Turbina ${unit}">
    <circle cx="${cx}" cy="${cy}" r="47" fill="url(#bodyMetal)" stroke="#a2b7cd" stroke-width="2"/>
    <circle cx="${cx}" cy="${cy}" r="38" fill="${color}" fill-opacity=".18" stroke="${color}" stroke-width="1.8"/>
    ${rotor(cx,cy,31,unit,'turbine')}
    <path d="M${mirror?cx+37:cx-56} 498H${mirror?cx+56:cx-37}V518H${mirror?cx+37:cx-56}Z" fill="${color}" fill-opacity=".24" stroke="#c0cbd9" stroke-width="1.3"/>
    <path d="M${cx-10} 545H${cx+10}V564H${cx-10}Z" fill="${color}" fill-opacity=".24" stroke="#c0cbd9" stroke-width="1.3"/>
  </g>`;
}
function preburner(cx,color,fuelRich) {
  const id=fuelRich?'pb-fuel':'pb-oxygen';
  return `<g aria-label="Prebruciatore ${fuelRich?'ricco di combustibile':'ricco di ossigeno'}">
    <path d="M${cx-35} 407H${cx+35}V468Q${cx+35} 503 ${cx+12} 521H${cx-12}Q${cx-35} 503 ${cx-35} 468Z" fill="#1f3042" stroke="#bfd0df" stroke-width="3"/>
    <path d="M${cx-25} 426H${cx+25}V470Q${cx+25} 496 ${cx+8} 513H${cx-8}Q${cx-25} 496 ${cx-25} 470Z" fill="${color}" fill-opacity=".25"/>
    <rect x="${cx-31}" y="415" width="62" height="10" fill="#9db1c3"/>
    ${[-21,-7,7,21].map(dx=>`<path d="M${cx+dx} 418V431" stroke="${fuelRich?C.fuel:C.lox}" stroke-width="4"/>`).join('')}
    <path d="M${cx-25} 440C${cx-13} 454 ${cx-21} 470 ${cx-7} 487C${cx-3} 476 ${cx+9} 469 ${cx+5} 451C${cx+22} 462 ${cx+12} 480 ${cx+22} 488L${cx+8} 504H${cx-10}Z" fill="${color}" opacity=".72" data-flicker="${id}"/>
    <path d="M${cx-38} 408H${cx+38}M${cx-38} 429H${cx+38}" stroke="#7f98ad" stroke-width="3"/>
    <rect x="${fuelRich?cx-43:cx+33}" y="447" width="10" height="18" fill="${fuelRich?C.lox:C.fuel}" stroke="#bfcfdd" stroke-width="1.3"/>
  </g>`;
}
let svg=`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="title desc">
<title id="title">Raptor: il principio del ciclo full-flow</title>
<desc id="desc">Schema concettuale originale del ciclo a combustione stadiata a flusso completo con metano e ossigeno. Due pompe, due prebruciatori, due turbine collegate meccanicamente alle rispettive pompe. Piccole alimentazioni incrociate. Entrambi i flussi gassosi raggiungono la camera principale. A destra un dettaglio separato del raffreddamento rigenerativo. Geometria, portate e movimento non in scala; non è un disegno costruttivo SpaceX.</desc>
<metadata>Rivoluzione Spaziale. Tavola originale, 11 ottobre 2026. CC BY 4.0. Fonti tecniche: NASA NTRS 19910021901, 20030003786, 20170005557; NASA Integrated Powerhead Demonstrator; SpaceX Starship. Nessuna immagine o diagramma di terzi incorporato. Schema concettuale, non costruttivo.</metadata>
<defs>
  <linearGradient id="background" x2="0" y2="1"><stop stop-color="#101c2d"/><stop offset="1" stop-color="#080f1a"/></linearGradient>
  <linearGradient id="bodyMetal" x2="1" y2="1"><stop stop-color="#445a70"/><stop offset=".32" stop-color="#273e53"/><stop offset="1" stop-color="#152638"/></linearGradient>
  <linearGradient id="bladeMetal" x2="1" y2="1"><stop stop-color="#e0eaf2"/><stop offset=".5" stop-color="#9fbbcc"/><stop offset="1" stop-color="#526d83"/></linearGradient>
  <linearGradient id="chamberHeat" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#ffb75b" stop-opacity=".45"/><stop offset=".36" stop-color="#ffc170" stop-opacity=".35"/><stop offset="1" stop-color="#f89839" stop-opacity=".1"/></linearGradient>
  <linearGradient id="plume" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#ffc66d" stop-opacity=".22"/><stop offset="1" stop-color="#ff9c48" stop-opacity="0"/></linearGradient>
  <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#45627a" stroke-opacity=".085" stroke-width="1"/></pattern>
  <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><path d="M0 0V6" stroke="#9db7cb" stroke-opacity=".6" stroke-width="1"/></pattern>
  <marker id="heatArrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#ffbb68"/></marker>
  <clipPath id="engineClip"><path d="M585 738H795V790C795 835 758 859 737 882C729 899 732 913 740 930C769 983 827 1021 860 1082H520C553 1021 611 983 640 930C648 913 651 899 643 882C622 859 585 835 585 790Z"/></clipPath>
</defs>
<g font-family="Segoe UI, Arial, sans-serif" stroke-linejoin="round">
<rect width="1800" height="1300" fill="url(#background)"/><rect x="44" y="174" width="1308" height="1032" fill="url(#grid)"/>
${text(55,47,'RIVOLUZIONE SPAZIALE / PROPULSIONE',17,C.muted,'letter-spacing="2.4" font-weight="600"')}
${text(55,106,'Raptor: il principio del ciclo full-flow',48,C.ink,'font-weight="650" letter-spacing="-.8"')}
${text(57,143,'Due prebruciatori, due turbine, una combustione finale. Nessuno scarico separato delle turbine.',23,C.muted)}
${line('M55 163H1745','#304458',1)}
${text(410,190,'METANO LIQUIDO · CH₄',22,C.fuel,'text-anchor="middle" font-weight="650"')}
${text(970,190,'OSSIGENO LIQUIDO · LOX',22,C.lox,'text-anchor="middle" font-weight="650"')}
${flow('fuel-inlet','M410 205V246',C.fuel,21,'liquid',6,37)}
${flow('lox-inlet','M970 205V246',C.lox,21,'liquid',6,37)}
${line('M404 214L410 221L416 214',C.fuel,2.5,'stroke-linecap="round"')}
${line('M964 214L970 221L976 214',C.lox,2.5,'stroke-linecap="round"')}
<!-- Ogni albero collega esclusivamente la propria turbina alla propria pompa. -->
${[410,970].map(cx=>`<g aria-label="Albero meccanico indipendente"><rect x="${cx-6}" y="322" width="12" height="149" fill="#688197" stroke="#bbcbd9" stroke-width="1"/><rect x="${cx-3}" y="333" width="6" height="126" fill="url(#hatch)"/><rect x="${cx-13}" y="338" width="26" height="11" rx="2" fill="#304d63" stroke="#acc0cf"/><rect x="${cx-13}" y="443" width="26" height="11" rx="2" fill="#304d63" stroke="#acc0cf"/></g>`).join('')}
${flow('fuel-pumped','M355 282H195Q175 282 175 302V412',C.fuel,21)}
${flow('lox-pumped','M1025 282H1185Q1205 282 1205 302V412',C.lox,21)}
${flow('fuel-cross','M270 282V337Q270 357 290 357H1177Q1192 357 1192 342Q1205 327 1218 342Q1218 357 1233 357H1275Q1295 357 1295 377V436Q1295 456 1275 456H1240',C.fuel,8,'liquid',6,140)}
${flow('lox-cross','M1100 282V343C1120 343 1120 371 1100 371V382Q1100 402 1080 402H203Q190 402 190 388Q175 373 160 388Q160 402 147 402H99Q79 402 79 422V436Q79 456 99 456H140',C.lox,8,'liquid',6,140)}
${dot(270,282,C.fuel)}${dot(1100,282,C.lox)}
${text(690,327,'Piccoli flussi incrociati',19,C.muted,'text-anchor="middle"')}
${flow('fuel-preburner-gas','M175 520V544Q175 563 195 563H346Q365 563 365 544V508H375',C.fr,22,'gas',6,90)}
${flow('lox-preburner-gas','M1205 520V544Q1205 563 1185 563H1034Q1015 563 1015 544V508H1005',C.ox,22,'gas',6,90)}
${flow('fuel-main-gas','M410 551V620Q410 645 435 645H575Q600 645 600 670V710',C.fr,24,'gas',6,86)}
${flow('lox-main-gas','M970 551V620Q970 645 945 645H805Q780 645 780 670V710',C.ox,24,'gas',6,86)}
${pump(410,C.fuel,'fuel','Pompa del metano')}${pump(970,C.lox,'oxygen','Pompa dell’ossigeno',true)}
${turbine(410,C.fr,'fuel')}${turbine(970,C.ox,'oxygen',true)}
${preburner(175,C.fr,true)}${preburner(1205,C.ox,false)}
<!-- Collegamenti fluidici interni ai componenti, ancora concettuali. -->
${flow('fuel-pump-inside','M410 240V265Q410 282 395 292Q377 302 358 282',C.fuel,3,'liquid',6,38)}
${flow('lox-pump-inside','M970 240V265Q970 282 985 292Q1003 302 1022 282',C.lox,3,'liquid',6,38)}
${flow('fuel-turbine-inside','M374 508Q381 532 405 538Q414 541 410 552',C.fr,3,'gas',6,38)}
${flow('lox-turbine-inside','M1006 508Q999 532 975 538Q966 541 970 552',C.ox,3,'gas',6,38)}
${flow('fuel-preburner-inside','M175 438V513',C.fr,3,'gas',6,39)}
${flow('lox-preburner-inside','M1205 438V513',C.ox,3,'gas',6,39)}
${leader('M467 270H490L501 254')}${text(507,248,'Pompa CH₄',23)}${text(507,279,'Aumenta la pressione',17,C.muted)}
${leader('M913 270H890L879 254')}${text(873,248,'Pompa LOX',23,C.ink,'text-anchor="end"')}${text(873,279,'Aumenta la pressione',17,C.muted,'text-anchor="end"')}
${leader('M416 423H457')}${text(465,423,'Albero',18,C.metal)}
${leader('M964 423H923')}${text(915,423,'Albero',18,C.metal,'text-anchor="end"')}
${leader('M456 507H479L493 493')}${text(499,490,'Turbina',23)}${text(499,518,'Aziona la pompa CH₄',17,C.muted)}
${leader('M924 507H901L887 493')}${text(881,490,'Turbina',23,C.ink,'text-anchor="end"')}${text(881,518,'Aziona la pompa LOX',17,C.muted,'text-anchor="end"')}
${lines(74,607,['Prebruciatore','ricco di combustibile'],22,C.fr,'font-weight="600"',29)}
${lines(74,672,['Metano + poco ossigeno','Combustione parziale'],18,C.muted,'',25)}
${leader('M175 524V585H115')}
${lines(1304,607,['Prebruciatore','ricco di ossigeno'],22,C.ox,'text-anchor="end" font-weight="600"',29)}
${lines(1304,672,['Ossigeno + poco metano','Combustione parziale'],18,C.muted,'text-anchor="end"',25)}
${leader('M1205 524V585H1254')}
${text(136,439,'LOX',16,C.lox,'text-anchor="end" font-weight="600"')}${text(1253,439,'CH₄',16,C.fuel,'font-weight="600"')}
${lines(306,726,['Gas ricco di','combustibile'],22,C.fr,'',29)}${leader('M469 719H496L533 646')}
${lines(1244,760,['Gas ricco di','ossigeno'],22,C.ox,'text-anchor="end"',29)}${leader('M1111 754H1090V635H966')}
<!-- Camera e ugello in sezione: entrambi i gas arrivano all’iniettore. -->
<path d="M520 1082H860L932 1196H447Z" fill="url(#plume)"/>
<path d="M585 738H795V790C795 835 758 859 737 882C729 899 732 913 740 930C769 983 827 1021 860 1082H520C553 1021 611 983 640 930C648 913 651 899 643 882C622 859 585 835 585 790Z" fill="url(#chamberHeat)" stroke="#b6c5d5" stroke-width="10"/>
<path d="M575 738H805V790C805 839 768 864 747 886C740 900 742 912 750 926C781 981 837 1025 871 1086M509 1086C543 1025 599 981 630 926C638 912 640 900 633 886C612 864 575 839 575 790V738" fill="none" stroke="#577187" stroke-width="2"/>
<rect x="580" y="701" width="220" height="15" rx="3" fill="#21394c" stroke="#bfd0de" stroke-width="2"/>
<path d="M591 704H687V715H591Z" fill="${C.fr}" fill-opacity=".4"/><path d="M693 704H789V715H693Z" fill="${C.ox}" fill-opacity=".4"/>
<rect x="578" y="716" width="224" height="20" fill="url(#bodyMetal)" stroke="#c1cfda" stroke-width="2"/>
${Array.from({length:12},(_,i)=>`<path d="M${591+i*18} 717V746" stroke="${i<6?C.fr:C.ox}" stroke-width="5"/>`).join('')}
<g clip-path="url(#engineClip)">
  ${[624,651,678,705,732,759].map((x,i)=>flow(`mix-${i}`,`M${x} 738L${690+(x-690)*.78} 790`,i<3?C.fr:C.ox,3,'gas',6,34)).join('')}
  ${[-2,-1,0,1,2].map((i)=>flow(`exhaust-${i}`,`M${690+i*30} 792C${690+i*33} 840 ${690+i*14} 867 ${690+i*12} 902C${690+i*12} 967 ${690+i*53} 1026 ${690+i*71} 1095`,C.fire,3,'exhaust',6,74)).join('')}
</g>
${flow('plume-center','M690 1086V1181',C.fire,2,'exhaust',6,57)}
${leader('M802 725H880L899 702')}${text(908,701,'Iniettore gas–gas',22)}
${leader('M796 793H899L922 808')}${lines(930,805,['Camera principale','La combustione si completa'],22,C.ink,'',29)}
${leader('M733 903H895L920 922')}${text(928,922,'Gola',22)}
${leader('M810 1015H906L930 1030')}${lines(938,1029,['Ugello','I gas si espandono','e accelerano'],22,C.ink,'',28)}
${text(434,883,'COMBUSTIONE',18,C.fire,'text-anchor="end" font-weight="600" letter-spacing="1.2"')}
${text(434,910,'FINALE',18,C.fire,'text-anchor="end" font-weight="600" letter-spacing="1.2"')}
${leader('M451 891H525L612 812')}<circle cx="612" cy="812" r="3" fill="${C.fire}"/>
${text(690,1168,'GAS VERSO L’ESTERNO',18,C.fire,'text-anchor="middle" font-weight="600" letter-spacing="1"')}
<!-- Legenda fissa, sempre leggibile durante l’animazione. -->
<rect x="1400" y="188" width="344" height="439" rx="14" fill="${C.panel}" stroke="#31465b"/>
${text(1426,224,'COME LEGGERE I FLUSSI',18,C.muted,'font-weight="650" letter-spacing=".8"')}
${line('M1426 245H1717','#31465b',1)}
${[[C.fuel,278,'Metano CH₄','prima del prebruciatore'],[C.lox,346,'Ossigeno LOX','prima del prebruciatore'],[C.fr,414,'Gas ricco di','combustibile'],[C.ox,482,'Gas ricco di','ossigeno'],[C.fire,550,'Gas di combustione','camera e ugello']].map(([c,y,a,b],i)=>`${line(`M1429 ${y-7}H1467`,c,6,i>1?'stroke-dasharray="3 5" stroke-linecap="round"':'stroke-linecap="round"')}${text(1484,y,a,21,c,'font-weight="600"')}${text(1484,y+25,b,17,C.muted)}`).join('')}
${line('M1429 602H1467',C.metal,4)}${text(1484,608,'Albero meccanico',20,C.metal)}
<rect x="1400" y="649" width="344" height="346" rx="14" fill="${C.panel}" stroke="#31465b"/>
${text(1426,685,'RAFFREDDAMENTO',20,C.ink,'font-weight="650"')}${text(1426,711,'Dettaglio funzionale separato',17,C.muted)}
${text(1475,752,'Gas caldi',17,C.fr,'text-anchor="middle"')}${text(1567,752,'Parete',17,C.metal,'text-anchor="middle"')}${text(1656,752,'CH₄',17,C.fuel,'text-anchor="middle"')}
<rect x="1438" y="766" width="107" height="151" rx="8" fill="${C.fr}" fill-opacity=".1"/>
<rect x="1555" y="766" width="23" height="151" fill="url(#bodyMetal)" stroke="#a6bacb"/><rect x="1558" y="766" width="17" height="151" fill="url(#hatch)"/>
${flow('coolant-detail','M1630 917V766',C.fuel,17,'liquid',6,46)}
${flow('hot-detail','M1474 771V912',C.fr,2,'exhaust',6,43)}
${[791,838,885].map(y=>line(`M1497 ${y}H1592`,C.fr,1.8,'marker-end="url(#heatArrow)" stroke-opacity=".7"')).join('')}
${text(1567,937,'Flusso di calore',14,C.fr,'text-anchor="middle"')}
${lines(1426,958,['Il metano assorbe calore','dalle pareti della camera e dell’ugello.'],17,C.muted,'',23)}
<rect x="1400" y="1017" width="344" height="187" rx="14" fill="${C.panel}" stroke="#31465b"/>
${text(1426,1054,'LIMITI DELLA TAVOLA',18,C.muted,'font-weight="650" letter-spacing=".7"')}
${lines(1426,1085,['Schema concettuale, non costruttivo.','Geometria e portate non in scala.','Velocità animate solo illustrative.','Omesse valvole e circuiti ausiliari.','Raffreddamento mostrato a parte.'],17,C.muted,'',23)}
${line('M55 1224H1745','#304458',1)}
${text(55,1256,'TAVOLA ORIGINALE · 11 OTTOBRE 2026 · CC BY 4.0',18,C.muted,'font-weight="600" letter-spacing=".8"')}
${text(55,1283,'Fonti tecniche: NASA / NTRS, dimostratore IPD e studi FFSC; SpaceX, Starship. Riferimenti e limiti nella pagina.',16,C.muted)}
${text(1744,1256,'RAPTOR / FULL-FLOW',18,C.muted,'text-anchor="end" font-weight="600" letter-spacing="1"')}
<g id="flow-tracers" pointer-events="none"></g>
</g></svg>`;
fs.mkdirSync(out,{recursive:true});
fs.writeFileSync(path.join(out,'raptor-full-flow-base.svg'),svg,'utf8');
fs.writeFileSync(path.join(out,'flussi.json'),JSON.stringify({width:W,height:H,loopSeconds:6,flows:flowSpecs},null,2),'utf8');
const animation=fs.readFileSync(path.join(out,'animazione.js'),'utf8');
const html=`<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Raptor full-flow · anteprima locale</title>
<style>*{box-sizing:border-box}body{margin:0;background:#070d16;color:#e7f0f7;font:16px 'Segoe UI',Arial,sans-serif}.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:12px;padding:15px 24px;border-bottom:1px solid #2a3c4e}.toolbar strong{margin-right:auto}button,a{font:inherit;color:#f0f5fa;background:#17293b;border:1px solid #43566b;border-radius:7px;padding:9px 14px;text-decoration:none;cursor:pointer}button:hover,a:hover{background:#223b50}button:focus-visible,a:focus-visible{outline:3px solid #69b9ff;outline-offset:3px}.hint{color:#a9bcce;font-size:14px}.stage{width:min(100%,1800px);margin:0 auto}.stage svg{display:block;width:100%;height:auto}.stage.full-size{width:1800px;max-width:none}footer{padding:18px 24px;text-align:center;color:#adbdcf;font-size:14px}footer a{border:0;background:none;padding:0;text-decoration:underline}@media(prefers-reduced-motion:reduce){.hint:after{content:' · movimento ridotto: usa Avvia'}}</style>
<div class="toolbar"><strong>Anteprima locale · tavola approvata</strong><button id="toggle" type="button">Pausa</button><button id="size" type="button">Dimensione originale</button><a href="raptor-full-flow.gif">Apri GIF</a><a href="raptor-full-flow.svg">Apri SVG</a><span class="hint">Animazione di flusso a regime; non è la sequenza di avviamento.</span></div>
<main class="stage">${svg}</main><footer>Schema originale del principio full-flow. Fonti, semplificazioni e istruzioni in <a href="LEGGIMI.md">LEGGIMI.md</a>.</footer>
<script>window.flowConfig=${JSON.stringify({loopSeconds:6,flows:flowSpecs})};</script><script>${animation}</script></html>`;
fs.writeFileSync(path.join(out,'anteprima.html'),html,'utf8');
console.log(`Creati SVG, configurazione dei flussi e anteprima: ${out}`);
