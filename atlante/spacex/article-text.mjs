const esc=x=>String(x).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
import {supplement,additionalContents} from './merlin-integrazioni.mjs';
export const sourceId=key=>'fonte-'+key.replace(/[^a-z0-9-]/gi,'-');
export function articleText(card){
 const sections=card.article?.sections;
 if(!sections)return card.sections.map(([title,text])=>`<section><h2>${esc(title)}</h2><p>${esc(text)}</p></section>`).join('');
 return `<article class="merlin-chapters" aria-label="Monografia tecnica Merlin">${sections.map(s=>{
  const refs=s.sources.map(key=>{
   const n=card.sources.indexOf(key)+1;
   if(!n)throw Error(`Fonte ${key} assente nella scheda Merlin`);
   return `<a class="source-ref" href="#${sourceId(key)}" aria-label="Fonte ${n}">[${n}]</a>`;
  }).join(' ');
  return `<section id="${esc(s.id)}"><h2>${esc(s.title)}</h2>${s.paragraphs.map(p=>`<p>${esc(p)}</p>`).join('')}<p class="chapter-references">${refs}</p>${supplement(card,s.id)}</section>`;
 }).join('')}${supplement(card,'end')}</article>`;
}
export function articleContents(card){
 if(!card.article)return '';
 return `<nav class="merlin-contents" aria-label="Indice della monografia"><h2>Indice</h2><ol>${additionalContents(card,'parameters')}${card.article.sections.map(s=>`<li><a href="#${esc(s.id)}">${esc(s.title)}</a></li>${additionalContents(card,s.id)}`).join('')}${additionalContents(card,'end')}</ol></nav>`;
}
