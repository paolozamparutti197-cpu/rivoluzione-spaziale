// I contenuti restano leggibili e navigabili anche senza JavaScript.
const form=document.querySelector('.filters');
if(form){const search=document.querySelector('#search'),family=document.querySelector('#family'),state=document.querySelector('#state'),cards=[...document.querySelectorAll('.card')];
 const normalize=x=>x.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 const filter=()=>{const q=normalize(search.value.trim());let n=0;for(const c of cards){c.hidden=!(normalize(c.dataset.search).includes(q)&&(!family.value||c.dataset.family===family.value)&&(!state.value||c.dataset.state===state.value));if(!c.hidden)n++;}document.querySelector('#results').textContent=`${n} ${n===1?'scheda disponibile':'schede disponibili'}`;document.querySelector('#empty').hidden=n!==0;};
 form.addEventListener('submit',e=>e.preventDefault());form.addEventListener('input',filter);form.addEventListener('change',filter);form.addEventListener('reset',()=>setTimeout(filter,0));
}
