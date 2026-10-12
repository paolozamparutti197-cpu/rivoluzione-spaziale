import {costModel,replacementModel} from './modelli.mjs';
const fmt=(v,d=1)=>v.toLocaleString('it-IT',{maximumFractionDigits:d,useGrouping:'always'});
document.querySelectorAll('form[data-model]').forEach(form=>{
 const output=form.querySelector('output'),error=form.querySelector('[data-error]');
 function update(event){
  event?.preventDefault();error.textContent='';
  if(!form.reportValidity())return;
  const values=Object.fromEntries(new FormData(form));
  try{
   if(form.dataset.model==='cost'){
    const m=costModel(values);
    output.textContent=`Costo medio: ${fmt(m.average,2)} unità convenzionali per volo. Stadio consumato a ogni volo: ${fmt(m.disposable,2)}. Rapporto: ${m.ratio==null?'non definito (base zero)':fmt(m.ratio*100,1)+'%'}.`;
   }else{
    const m=replacementModel(values);
    output.textContent=`Sostituzioni medie: ${fmt(m.perYear,1)} satelliti/anno, circa ${fmt(m.perDay,2)} al giorno. Scenario stazionario, non previsione di lanci o rientri.`;
   }
  }catch(e){error.textContent=e.message;output.textContent='Correggi i parametri per calcolare il modello.';}
 }
 form.addEventListener('submit',update);
 form.addEventListener('invalid',()=>{
  error.textContent='Uno o più parametri non rispettano i limiti indicati.';
  output.textContent='Risultato non ricalcolato: correggi i parametri.';
 },true);
 form.addEventListener('reset',()=>setTimeout(()=>update(),0));
});
