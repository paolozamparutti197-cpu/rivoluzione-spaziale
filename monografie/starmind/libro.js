document.querySelectorAll('.bookaside details').forEach(d=>{if(innerWidth<951)d.open=false;});
const format=(n,d=0)=>n.toLocaleString('it-IT',{minimumFractionDigits:d,maximumFractionDigits:d});
function thermal(){
 const ids=['heat-power','heat-temp','heat-epsilon','heat-bg'];const [p,t,e,b]=ids.map(x=>Number(document.getElementById(x).value));const out=document.getElementById('heat-result');
 if(ids.some(x=>!document.getElementById(x).checkValidity())||!ids.every(x=>document.getElementById(x).value.trim())||![p,t,e,b].every(Number.isFinite)||p<=0||e<=0||e>1||t<=b){out.textContent='Inserisci valori validi: potenza positiva, emissività fra 0 e 1 e radiatore più caldo del fondo.';return;}
 const area=p*1000/(e*5.670374419e-8*(t**4-b**4));out.textContent='Superficie radiante efficace: '+format(area,1)+' m². Flusso netto: '+format(p*1000/area,1)+' W/m². Temperatura: '+format(t-273.15,1)+' °C. Modello ideale, senza Sole, Terra, margini o circuito interno.';
}
if(document.getElementById('lab-termico')){
 document.querySelectorAll('#lab-termico input').forEach(x=>x.addEventListener('input',thermal));document.getElementById('heat-reset').addEventListener('click',()=>{['heat-power','heat-temp','heat-epsilon','heat-bg'].forEach((x,i)=>document.getElementById(x).value=[175,350,.9,0][i]);thermal();});thermal();
}
function fleet(){
 const ids=['fleet-n','fleet-mass','fleet-payload','fleet-factor','fleet-life'];const [n,m,p,f,l]=ids.map(x=>Number(document.getElementById(x).value));const out=document.getElementById('fleet-result');
 if(ids.some(x=>!document.getElementById(x).checkValidity())||!ids.every(x=>document.getElementById(x).value.trim())||![n,m,p,f,l].every(Number.isFinite)||n<1||!Number.isInteger(n)||m<=0||p<=0||f<=0||f>1||l<=0){out.textContent='Inserisci valori validi: numero intero di satelliti, masse e vita positive, frazione utile fra 0 e 1.';return;}
 const per=Math.floor(p*f/m);if(per<1){out.textContent='Nessun satellite entra nel carico utile ipotizzato. Aumenta il carico o riduci massa e riserve.';return;}
 const initial=Math.ceil(n/per),replace=n/l,launches=Math.ceil(replace/per);out.textContent=format(per)+' satelliti per lancio (limite di massa). Almeno '+format(initial)+' lanci per il dispiegamento; '+format(n*m)+' t di satelliti. In regime stazionario: circa '+format(replace,1)+' sostituzioni/anno e '+format(launches)+' lanci/anno ('+format(launches/365,2)+' al giorno). Sono ipotesi; volume e traiettoria possono peggiorare il risultato.';
}
if(document.getElementById('lab-logistica')){
 document.querySelectorAll('#lab-logistica input').forEach(x=>x.addEventListener('input',fleet));document.getElementById('fleet-reset').addEventListener('click',()=>{['fleet-n','fleet-mass','fleet-payload','fleet-factor','fleet-life'].forEach((x,i)=>document.getElementById(x).value=[1000,4,100,.8,5][i]);fleet();});fleet();
}
const search=document.getElementById('cerca-cronologia'),type=document.getElementById('tipo-cronologia');
function filter(){const q=search.value.trim().toLocaleLowerCase('it');let n=0;document.querySelectorAll('#cronologia tbody tr').forEach(r=>{const show=r.textContent.toLocaleLowerCase('it').includes(q)&&(!type.value||r.dataset.tipo===type.value);r.hidden=!show;if(show)n++;});document.getElementById('risultati').textContent=n+' eventi visualizzati';document.getElementById('nessun-evento').hidden=n!==0;}
if(search){search.addEventListener('input',filter);type.addEventListener('change',filter);document.getElementById('reset-cronologia').addEventListener('click',()=>{search.value='';type.value='';filter();});filter();}
