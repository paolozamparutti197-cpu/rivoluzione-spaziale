/* Tavola originale: topologia funzionale, non sezione costruttiva del Merlin. */
const fs=require('node:fs'), path=require('node:path');
const out=__dirname, W=1800, H=1300;
const C={bg:'#0a111d',panel:'#101c2c',edge:'#31465b',ink:'#f1f6fb',muted:'#adbdcf',fuel:'#51dfba',lox:'#69b9ff',gas:'#ffbb68',fire:'#ffe19a',metal:'#bfccd8'};
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const text=(x,y,s,size=22,fill=C.ink,extra='')=>`<text x="${x}" y="${y}" font-size="${size}" fill="${fill}" ${extra}>${esc(s)}</text>`;
const lines=(x,y,ss,size=22,fill=C.ink,extra='',gap=size*1.3)=>ss.map((s,i)=>text(x,y+i*gap,s,size,fill,extra)).join('');
const line=(d,stroke=C.muted,width=1.5,extra='')=>`<path d="${d}" fill="none" stroke="${stroke}" stroke-width="${width}" ${extra}/>`;
const leader=d=>line(d,'#8398af',1.5,'stroke-linecap="round"');
const dot=(x,y,c)=>`<circle cx="${x}" cy="${y}" r="6" fill="${c}" stroke="${C.bg}" stroke-width="2"/>`;
const flowSpecs=[];
function flow(id,d,color,width=19,kind='liquid',spacing=88){
 flowSpecs.push({id,d,color,width,kind,period:6,spacing});
 if(width<=3)return `<path id="${id}" d="${d}" fill="none" stroke="${color}" stroke-width="1" stroke-opacity=".2" data-flow="true"/>`;
 return `<g class="conduit">${line(d,C.bg,width+11,'stroke-linecap="round" stroke-linejoin="round"')}${line(d,C.edge,width+5,'stroke-linecap="round" stroke-linejoin="round"')}${line(d,color,width,'stroke-opacity=".27" stroke-linecap="round" stroke-linejoin="round"')}${kind==='gas'?line(d,color,2,'stroke-opacity=".45" stroke-dasharray="2 8" stroke-linecap="round"'):''}<path id="${id}" d="${d}" fill="none" stroke="transparent" data-flow="true"/></g>`;
}
function rotor(cx,cy,r,type){
 const n=type==='pump'?7:12;
 let blades='';for(let i=0;i<n;i++){
  const d=type==='pump'?`M5 -${r-4} C${r*.65} -${r*.83} ${r*.56} -${r*.23} 8 -7 L2 -12 C${r*.18} -${r*.37} ${r*.28} -${r*.6} 0 -${r-4} Z`:`M-4 -${r-3} L7 -${r-4} L11 -${r*.47} L1 -${r*.36} Z`;
  blades+=`<path d="${d}" transform="rotate(${i*360/n})" fill="url(#bladeMetal)" stroke="#9cb0c4" stroke-width=".7"/>`;
 }
 return `<g data-rotor="common-shaft" data-cx="${cx}" data-cy="${cy}" transform="translate(${cx} ${cy})">${blades}<circle r="9" fill="#d8e5ee" stroke="#647b90" stroke-width="2"/><circle r="3" fill="#233549"/></g>`;
}
function machine(cx,color,type){
 const cy=300,r=type==='pump'?57:47;
 return `<g><circle cx="${cx}" cy="${cy}" r="${r}" fill="url(#bodyMetal)" stroke="#afc3d6" stroke-width="2"/><circle cx="${cx}" cy="${cy}" r="${r-10}" fill="${color}" fill-opacity=".16" stroke="${color}" stroke-opacity=".7" stroke-width="2"/><circle cx="${cx}" cy="${cy}" r="36" fill="#101b2a" stroke="#829bb0" stroke-width="1.3"/>${rotor(cx,cy,type==='pump'?33:31,type)}<rect x="${cx-10}" y="${cy-r-4}" width="20" height="24" fill="${color}" fill-opacity=".28" stroke="#b9d0de" stroke-width="1.4"/><rect x="${cx-10}" y="${cy+r-18}" width="20" height="25" fill="${color}" fill-opacity=".28" stroke="#b9d0de" stroke-width="1.4"/>${[45,135,225,315].map(a=>`<circle cx="${cx+(r-5)*Math.cos(a*Math.PI/180)}" cy="${cy+(r-5)*Math.sin(a*Math.PI/180)}" r="2.5" fill="#b8c6d5"/>`).join('')}</g>`;
}
const chamber='M585 750H795V800C795 840 758 866 737 889C729 905 732 919 740 936C769 987 827 1025 860 1086H520C553 1025 611 987 640 936C648 919 651 905 643 889C622 866 585 840 585 800Z';
let svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1300" viewBox="0 0 1800 1300" role="img" aria-labelledby="title desc">
<title id="title">Merlin: il circuito a generatore di gas</title>
<desc id="desc">Ossigeno liquido e cherosene RP-1 alimentano due pompe azionate da una turbina sul medesimo albero. Due piccole derivazioni alimentano un generatore di gas. I gas passano nella turbina e vengono scaricati fuori dalla camera principale. Il cherosene principale assorbe calore nelle pareti e raggiunge l'iniettore, distinto dall'alimentazione dell'ossigeno. Schema funzionale originale, non disegno costruttivo SpaceX.</desc>
<metadata>Rivoluzione Spaziale, 11 ottobre 2026. CC BY 4.0. Fonti: SpaceX Falcon User's Guide 2025, sezione 2.3; NASA-CR-184205, sezione 2.1.1.1. Nessuna grafica di terzi incorporata. Disposizione, collegamenti dei canali e velocità illustrativi.</metadata>
<defs>
<linearGradient id="background" x2="0" y2="1"><stop stop-color="#101c2d"/><stop offset="1" stop-color="#080f1a"/></linearGradient>
<linearGradient id="bodyMetal" x2="1" y2="1"><stop stop-color="#445a70"/><stop offset=".32" stop-color="#273e53"/><stop offset="1" stop-color="#152638"/></linearGradient>
<linearGradient id="bladeMetal" x2="1" y2="1"><stop stop-color="#e0eaf2"/><stop offset=".5" stop-color="#9fbbcc"/><stop offset="1" stop-color="#526d83"/></linearGradient>
<linearGradient id="chamberHeat" x2="0" y2="1"><stop stop-color="#ffb75b" stop-opacity=".45"/><stop offset=".36" stop-color="#ffc170" stop-opacity=".35"/><stop offset="1" stop-color="#f89839" stop-opacity=".1"/></linearGradient>
<linearGradient id="plume" x2="0" y2="1"><stop stop-color="#ffc66d" stop-opacity=".22"/><stop offset="1" stop-color="#ff9c48" stop-opacity="0"/></linearGradient>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#45627a" stroke-opacity=".085"/></pattern>
<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><path d="M0 0V6" stroke="#9db7cb" stroke-opacity=".6"/></pattern>
<marker id="heatArrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="#ffbb68"/></marker>
<clipPath id="engineClip"><path d="${chamber}"/></clipPath>
</defs><g font-family="Segoe UI, Arial, sans-serif" stroke-linejoin="round">
<rect width="1800" height="1300" fill="url(#background)"/><rect x="44" y="174" width="1308" height="1032" fill="url(#grid)"/>
${text(55,47,'RIVOLUZIONE SPAZIALE / PROPULSIONE',17,C.muted,'letter-spacing="2.4" font-weight="600"')}
${text(55,106,'Merlin: il circuito a generatore di gas',48,C.ink,'font-weight="650" letter-spacing="-.8"')}
${text(57,143,'Due pompe, una turbina, un solo albero. I gas della turbina non rientrano nella camera principale.',23,C.muted)}
${line('M55 163H1745','#304458',1)}
${text(370,198,'OSSIGENO LIQUIDO · LOX',22,C.lox,'text-anchor="middle" font-weight="650"')}
${text(1070,198,'CHEROSENE · RP-1',22,C.fuel,'text-anchor="middle" font-weight="650"')}
${text(700,200,'TURBINA',22,C.gas,'text-anchor="middle" font-weight="650"')}
${flow('lox-inlet','M370 216V260',C.lox,21,'liquid',38)}
${flow('fuel-inlet','M1070 216V260',C.fuel,21,'liquid',38)}
<!-- Un solo collegamento meccanico; non rappresenta una condotta. -->
<rect x="370" y="294" width="700" height="12" fill="#688197" stroke="#bbcbd9"/><rect x="380" y="298" width="680" height="4" fill="url(#hatch)"/>
${[460,600,800,970].map(x=>`<rect x="${x}" y="287" width="14" height="26" rx="2" fill="#304d63" stroke="#acc0cf"/>`).join('')}
${flow('lox-main','M370 343V661Q370 689 398 689H600Q615 689 615 704V717',C.lox,23)}
${flow('fuel-main','M1070 343V390Q1070 416 1096 416H1114Q1140 416 1140 442V1054Q1140 1086 1108 1086H872',C.fuel,23)}
<!-- Derivazioni reali: solo qui compaiono i punti di raccordo. -->
${flow('lox-gg-feed','M370 490H640Q665 490 665 515V543',C.lox,8,'liquid',95)}
${flow('fuel-gg-feed','M1140 490H760Q735 490 735 515V543',C.fuel,8,'liquid',95)}
${dot(370,490,C.lox)}${dot(1140,490,C.fuel)}
<!-- Due ponti: incrocio di tubazioni, NON connessione. -->
${flow('gg-to-turbine','M745 601H900Q930 601 930 571V518Q930 505 945 505Q960 490 945 475Q930 475 930 462V256Q930 230 904 230H720Q700 230 700 250V265',C.gas,21,'gas',92)}
${flow('turbine-exhaust','M700 340V400Q700 425 675 425H398Q384 425 384 411Q370 397 356 411Q356 425 342 425H173Q145 425 145 453V1082',C.gas,22,'gas',90)}
${machine(370,C.lox,'pump')}${machine(700,C.gas,'turbine')}${machine(1070,C.fuel,'pump')}
${leader('M324 332L294 358H276')}${text(269,365,'Pompa LOX',23,C.ink,'text-anchor="end"')}
${leader('M1116 332L1142 360H1158')}${text(1166,366,'Pompa RP-1',23)}
${leader('M487 306V331')}${text(487,354,'Un solo albero',20,C.metal,'text-anchor="middle"')}
${leader('M743 330H760L778 349')}${lines(789,366,['Aziona le due','pompe'],18,C.muted,'',24)}
${leader('M949 564H979L992 548')}${lines(1000,548,['Gas verso','la turbina'],18,C.gas,'',24)}
${text(700,461,'PICCOLE DERIVAZIONI',17,C.muted,'text-anchor="middle" letter-spacing="1"')}
<!-- Generatore: due ingressi liquidi distinti e un'uscita gassosa. -->
<path d="M650 536H750V604Q750 636 716 642H684Q650 636 650 604Z" fill="#1f3042" stroke="#bfd0df" stroke-width="3"/>
<path d="M660 552H740V603Q740 627 714 632H686Q660 627 660 603Z" fill="${C.gas}" fill-opacity=".26"/>
<rect x="647" y="536" width="106" height="16" fill="url(#bodyMetal)" stroke="#b9c7d4"/>
<path d="M661 537V560M671 537V560" stroke="${C.lox}" stroke-width="4"/><path d="M730 537V560M740 537V560" stroke="${C.fuel}" stroke-width="4"/>
<path d="M663 568Q681 580 679 598Q687 588 698 574Q715 590 712 605Q723 593 736 598Q731 617 713 626H686Q669 617 663 568Z" fill="${C.gas}" opacity=".68"/>
<rect x="738" y="591" width="20" height="20" fill="${C.gas}" fill-opacity=".3" stroke="#bdcedb"/>
${flow('gg-inside','M700 559V586Q700 601 720 601H745',C.gas,3,'gas',32)}
${leader('M649 586H612L596 568')}${text(589,564,'Generatore di gas',22,C.ink,'text-anchor="end"')}${lines(589,592,['Una piccola parte','dei due propellenti'],18,C.muted,'text-anchor="end"',25)}
${text(238,913,'SCARICO',21,C.gas,'font-weight="600"')}${text(238,942,'DELLA TURBINA',21,C.gas,'font-weight="600"')}
${lines(238,978,['I gas hanno ceduto energia.','Escono dal circuito senza','entrare nella camera principale.'],18,C.muted,'',25)}
${leader('M227 932H190L145 964')}
<path d="M123 1086H167L185 1170H105Z" fill="url(#plume)"/>
${flow('turbine-plume','M145 1086V1157',C.gas,2,'exhaust',38)}
${text(145,1190,'USCITA SEPARATA',17,C.gas,'text-anchor="middle" font-weight="600"')}
<!-- Camera e ugello, con camicia schematizzata sulla parete destra. -->
<path d="M520 1086H860L932 1196H447Z" fill="url(#plume)"/>
<path d="${chamber}" fill="url(#chamberHeat)" stroke="#b6c5d5" stroke-width="10"/>
<path d="M575 750H805V800C805 844 768 871 747 893C740 907 742 919 750 932C781 985 837 1029 872 1086M508 1086C543 1029 599 985 630 932C638 919 640 907 633 893C612 871 575 844 575 800V750" fill="none" stroke="#577187" stroke-width="2"/>
${flow('cooling-main','M872 1086C837 1029 781 985 750 932C742 919 740 907 747 893C768 871 805 844 805 800V750',C.fuel,8,'liquid',58)}
${flow('fuel-warmed','M805 750V697Q805 681 789 681H776Q760 681 760 697V717',C.fuel,17,'liquid',53)}
<rect x="580" y="713" width="220" height="18" rx="3" fill="#21394c" stroke="#bfd0de" stroke-width="2"/>
<path d="M591 716H687V729H591Z" fill="${C.lox}" fill-opacity=".4"/><path d="M693 716H789V729H693Z" fill="${C.fuel}" fill-opacity=".4"/>
<rect x="578" y="731" width="224" height="17" fill="url(#bodyMetal)" stroke="#c1cfda" stroke-width="2"/>
<path d="M685 727H705V760L714 773H676L685 760Z" fill="url(#bladeMetal)" stroke="#c5d3df" stroke-width="1.5"/>
<g clip-path="url(#engineClip)">
${flow('lox-spray','M675 753Q639 775 620 803',C.lox,3,'liquid',36)}
${flow('fuel-spray','M719 753Q751 775 769 803',C.fuel,3,'liquid',36)}
${[-2,-1,0,1,2].map(i=>flow(`exhaust-${i}`,`M${690+i*30} 803C${690+i*33} 850 ${690+i*14} 873 ${690+i*12} 909C${690+i*12} 972 ${690+i*53} 1030 ${690+i*71} 1099`,C.fire,3,'exhaust',74)).join('')}
</g>
${flow('main-plume','M690 1090V1181',C.fire,2,'exhaust',57)}
${leader('M704 741H851L876 724')}${text(882,726,'Iniettore a pintle',22)}
${leader('M795 802H885L906 818')}${text(914,817,'Camera principale',22)}${text(914,846,'Brucia LOX e RP-1',20,C.muted)}
${leader('M641 911H552L536 925')}${text(526,929,'Gola',22,C.ink,'text-anchor="end"')}
${leader('M811 1019H930L951 999')}${text(959,996,'Ugello',22)}${text(959,1025,'Espansione dei gas',18,C.muted)}
${leader('M793 841H877L899 873')}<circle cx="793" cy="841" r="3" fill="${C.fuel}"/>${lines(907,879,['RP-1 nelle pareti','Assorbe calore e risale','verso l’iniettore'],18,C.fuel,'',25)}
${text(690,1172,'SCARICO PRINCIPALE',18,C.fire,'text-anchor="middle" font-weight="600" letter-spacing="1"')}
<!-- Pannelli: testo e legenda restano invarianti in tutti i fotogrammi. -->
<rect x="1400" y="188" width="344" height="439" rx="14" fill="${C.panel}" stroke="#31465b"/>
${text(1426,224,'COME LEGGERE I FLUSSI',18,C.muted,'font-weight="650" letter-spacing=".8"')}${line('M1426 245H1717','#31465b',1)}
${[[C.lox,278,'Ossigeno LOX','ossidante liquido'],[C.fuel,355,'Cherosene RP-1','combustibile / refrigerante'],[C.gas,432,'Gas del generatore','prima e dopo la turbina'],[C.fire,509,'Gas della camera','scarico principale']].map(([c,y,a,b],i)=>`${line(`M1429 ${y-7}H1467`,c,6,i>1?'stroke-dasharray="3 5" stroke-linecap="round"':'stroke-linecap="round"')}${text(1484,y,a,21,c,'font-weight="600"')}${text(1484,y+25,b,17,C.muted)}`).join('')}
${line('M1429 587H1467',C.metal,4)}${text(1484,593,'Albero meccanico',20,C.metal)}
<rect x="1400" y="649" width="344" height="346" rx="14" fill="${C.panel}" stroke="#31465b"/>
${text(1426,685,'RAFFREDDAMENTO',20,C.ink,'font-weight="650"')}${text(1426,711,'Dettaglio della parete',17,C.muted)}
${text(1475,752,'Gas caldi',17,C.fire,'text-anchor="middle"')}${text(1567,752,'Parete',17,C.metal,'text-anchor="middle"')}${text(1656,752,'RP-1',17,C.fuel,'text-anchor="middle"')}
<rect x="1438" y="766" width="107" height="151" rx="8" fill="${C.fire}" fill-opacity=".1"/><rect x="1555" y="766" width="23" height="151" fill="url(#bodyMetal)" stroke="#a6bacb"/><rect x="1558" y="766" width="17" height="151" fill="url(#hatch)"/>
${flow('coolant-detail','M1630 917V766',C.fuel,17,'liquid',46)}${flow('hot-detail','M1474 771V912',C.fire,2,'exhaust',43)}
${[791,838,885].map(y=>line(`M1497 ${y}H1592`,C.gas,1.8,'marker-end="url(#heatArrow)" stroke-opacity=".7"')).join('')}
${text(1567,937,'Flusso di calore',14,C.gas,'text-anchor="middle"')}${lines(1426,958,['Il cherosene sottrae calore alle pareti,','poi alimenta la combustione.'],17,C.muted,'',23)}
<rect x="1400" y="1017" width="344" height="187" rx="14" fill="${C.panel}" stroke="#31465b"/>
${text(1426,1054,'LIMITI DELLA TAVOLA',18,C.muted,'font-weight="650" letter-spacing=".7"')}${lines(1426,1085,['Schema funzionale, non costruttivo.','Rotori affiancati per chiarezza.','Geometria e portate non in scala.','Valvole e avviamento omessi.','Canali di raffreddamento simbolici.'],17,C.muted,'',23)}
${line('M55 1224H1745','#304458',1)}
${text(55,1256,'TAVOLA ORIGINALE · 11 OTTOBRE 2026 · CC BY 4.0',18,C.muted,'font-weight="600" letter-spacing=".8"')}
${text(55,1283,'Fonti tecniche: SpaceX, Falcon User’s Guide 2025, §2.3; NASA-CR-184205, §2.1.1.1. Riferimenti e limiti nella pagina.',16,C.muted)}
${text(1744,1256,'MERLIN / GAS GENERATOR',18,C.muted,'text-anchor="end" font-weight="600" letter-spacing="1"')}
<g id="flow-tracers" pointer-events="none"></g></g></svg>`;
fs.writeFileSync(path.join(out,'merlin-ciclo-gas-base.svg'),svg,'utf8');
fs.writeFileSync(path.join(out,'flussi.json'),JSON.stringify({width:W,height:H,loopSeconds:6,flows:flowSpecs},null,2),'utf8');
const animation=fs.readFileSync(path.join(out,'animazione.js'),'utf8');
const html=`<!doctype html><html lang="it"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Merlin · circuito animato</title><style>*{box-sizing:border-box}body{margin:0;background:#070d16;color:#e7f0f7;font:16px 'Segoe UI',Arial,sans-serif}.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:12px;padding:15px 24px;border-bottom:1px solid #2a3c4e}.toolbar strong{margin-right:auto}button,a{font:inherit;color:#f0f5fa;background:#17293b;border:1px solid #526c84;border-radius:5px;padding:8px 12px;text-decoration:none;cursor:pointer}.stage{overflow:auto}.stage svg{display:block;width:100%;height:auto}.stage.full-size svg{width:1800px;max-width:none}footer{padding:18px;color:#adbdcf}</style><div class="toolbar"><strong>Merlin · circuito a generatore di gas</strong><button id="toggle">Pausa</button><button id="size">Dimensione originale</button><a href="merlin-ciclo-gas.gif">Apri GIF</a><a href="merlin-ciclo-gas.svg">Apri SVG</a></div><main class="stage">${svg}</main><footer>Flussi a regime: non è una sequenza di accensione. Fonti e limiti in <a href="LEGGIMI.md">LEGGIMI.md</a>.</footer><script>window.flowConfig=${JSON.stringify({loopSeconds:6,flows:flowSpecs})};</script><script>${animation}</script></html>`;
fs.writeFileSync(path.join(out,'anteprima.html'),html,'utf8');
console.log('Creati tavola Merlin, percorsi e anteprima locale.');
