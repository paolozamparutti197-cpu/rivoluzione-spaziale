// Integrazioni additive della sola monografia Merlin. I testi originari restano separati.
const esc=x=>String(x).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const sourceId=key=>'fonte-'+key.replace(/[^a-z0-9-]/gi,'-');
function refs(card,keys=[]){
 return keys.map(key=>{
  const n=card.sources.indexOf(key)+1;
  if(!n)throw Error(`Fonte integrativa assente: ${key}`);
  return `<a class="source-ref" href="#${sourceId(key)}" aria-label="Fonte ${n}">[${n}]</a>`;
 }).join(' ');
}
function cell(card,item){
 if(typeof item==='string')return esc(item);
 return `${item.value?`<strong class="merlin-value">${esc(item.value)}</strong>`:''}${item.text?`<span>${esc(item.text)}</span>`:''}${item.sources?.length?` <span class="merlin-cell-refs">${refs(card,item.sources)}</span>`:''}`;
}
function block(card,b,level=3){
 const heading=`h${level}`;
 const paragraphs=(b.paragraphs||[]).map(p=>`<p>${cell(card,p)}</p>`).join('');
 const table=b.columns?`<p class="merlin-table-context">${esc(b.caption)}</p><p class="merlin-scroll-hint">Su schermi stretti, scorri la tabella orizzontalmente. Puoi selezionarla anche con la tastiera.</p><div class="table-scroll merlin-table-scroll" tabindex="0" role="region" aria-labelledby="${esc(b.id)}-caption"><table class="merlin-table${b.wide?' merlin-table--wide':''}"><caption id="${esc(b.id)}-caption">${esc(b.title)}</caption><thead><tr>${b.columns.map(x=>`<th scope="col">${esc(x)}</th>`).join('')}</tr></thead><tbody>${b.rows.map(row=>`<tr>${row.map((v,i)=>i?`<td>${cell(card,v)}</td>`:`<th scope="row">${cell(card,v)}</th>`).join('')}</tr>`).join('')}</tbody></table></div>`:'';
 const notes=(b.notes||[]).map(p=>`<p class="merlin-method-note">${cell(card,p)}</p>`).join('');
 const glossary=b.terms?`<dl class="merlin-glossary">${b.terms.map(([term,definition])=>`<div><dt>${esc(term)}</dt><dd>${esc(definition)}</dd></div>`).join('')}</dl>`:'';
 const links=b.links?`<p class="merlin-reading-links">${b.links.map(([url,label])=>`<a href="${esc(url)}">${esc(label)}</a>`).join(' · ')}</p>`:'';
 return `<section class="merlin-addition" id="${esc(b.id)}"><${heading}>${esc(b.title)}</${heading}>${paragraphs}${table}${notes}${glossary}${links}</section>`;
}
export function supplement(card,placement){
 return (card.integration?.blocks||[]).filter(b=>b.placement===placement).map(b=>block(card,b,placement==='parameters'||placement==='end'?2:3)).join('');
}
export function brief(card){
 const b=card.integration?.brief;
 return b?`<aside class="merlin-brief" aria-labelledby="merlin-in-breve"><h2 id="merlin-in-breve">In breve</h2><p>${esc(b)}</p></aside>`:'';
}
export function authenticPhoto(card){
 const p=card.integration?.photograph;
 if(!p)return '';
 return `<figure class="merlin-authentic" id="merlin-fotografia-originale"><img src="${esc(p.src)}" width="${p.width}" height="${p.height}" loading="lazy" decoding="async" alt="${esc(p.alt)}"><figcaption><h3>Il motore reale al banco</h3><p>${esc(p.caption)}</p><span class="credit">SpaceX · circa 2012 · <a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0</a>. <a href="${esc(p.source)}">Fonte, licenza e attribuzione</a>. Fotografia riprodotta integralmente, senza ritocchi.</span></figcaption></figure>`;
}
export function additionalContents(card,placement){
 return (card.integration?.blocks||[]).filter(b=>b.placement===placement).map(b=>`<li class="merlin-contents-addition"><a href="#${esc(b.id)}">${esc(b.title)}</a></li>`).join('');
}
