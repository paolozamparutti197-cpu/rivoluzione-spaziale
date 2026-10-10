"""Generatore circoscritto alla monografia Starlink; conserva il resto del sito."""
from pathlib import Path
from html import escape
import json,re,csv
ROOT=Path(__file__).resolve().parents[1]
BOOK=ROOT/'monografie'/'starlink'
data=json.loads((BOOK/'libro.json').read_text(encoding='utf-8'))
chapters=data['capitoli']
sources=json.loads((BOOK/'fonti.json').read_text(encoding='utf-8'))
events=json.loads((BOOK/'cronologia.json').read_text(encoding='utf-8'))
timeline='<div class="table-wrap" tabindex="0" role="region" aria-label="Cronologia Starlink"><table id="cronologia"><caption>Tappe selezionate, edizione 10 ottobre 2026</caption><thead><tr><th>Data</th><th>Tappa</th><th>Fonte</th></tr></thead><tbody>'+''.join(f'<tr><td>{escape(date)}</td><td>{escape(event)}</td><td><a href="{escape(sources[key][1],quote=True)}">Documento</a></td></tr>' for date,event,key in events)+'</tbody></table></div>'
with (BOOK/'cronologia.csv').open('w',encoding='utf-8-sig',newline='') as stream:
 writer=csv.writer(stream);writer.writerow(['Data','Tappa','Fonte']);writer.writerows((date,event,sources[key][1]) for date,event,key in events)
def toc(current=None):
 return '<ol class="toc">'+''.join(f'<li><a href="{slug}.html"'+(' aria-current="page"' if slug==current else '')+f'><span class="number">{i:02}</span>{escape(title)}</a></li>' for i,(slug,title,desc) in enumerate(chapters,1) if (BOOK/'contenuti'/f'{slug}.html').exists())+'</ol>'
def header(title,desc):
 return f'<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} | Rivoluzione Spaziale</title><meta name="description" content="{escape(desc,quote=True)}"><link rel="stylesheet" href="libro.css"><script src="libro.js" defer></script></head><body><a class="skip" href="#contenuto">Vai al testo</a><header class="bookbar"><a class="brand" href="../../index.html">Rivoluzione <span>Spaziale</span></a><nav aria-label="Navigazione principale"><a href="../../sezioni/spacex.html">SpaceX</a><a href="../../sezioni/monografie-spacex.html">Monografie</a><a href="index.html">Indice del libro</a></nav></header>'
def end():
 return '<footer>Rivoluzione Spaziale · Monografia Starlink · Edizione del 10 ottobre 2026.<br>Pubblicazione indipendente. I dati dichiarati dai fornitori non sono una garanzia di prestazioni.<br><a href="crediti.html">Fonti, immagini e criteri</a> · <a href="index.html">Indice completo</a></footer></body></html>'
def references(body):
 ids=re.findall(r'<!-- FONTI:([^>]+) -->',body)
 if not ids:return body
 keys=ids[0].split()
 entries=''.join(f'<li><a href="{escape(sources[k][1],quote=True)}">{escape(sources[k][0])}</a>. {escape(sources[k][2])}</li>' for k in keys)
 return re.sub(r'<!-- FONTI:[^>]+ -->','<section class="sources"><h2>Fonti pubbliche e tracce</h2><ul>'+entries+'</ul></section>',body)
total=0
for i,(slug,title,desc) in enumerate(chapters):
 source=BOOK/'contenuti'/f'{slug}.html'
 if not source.exists():continue
 body=references(source.read_text(encoding='utf-8').replace('<!-- CRONOLOGIA -->',timeline))
 words=len(re.findall(r"\b[\wÀ-ÿ’]+\b",re.sub('<[^>]+>',' ',body)));total+=words
 links=[]
 for rel,j in [('prev',i-1),('next',i+1)]:
  if 0<=j<len(chapters) and (BOOK/'contenuti'/f'{chapters[j][0]}.html').exists():links.append(f'<a class="button" rel="{rel}" href="{chapters[j][0]}.html">{escape(chapters[j][1])}</a>')
 page=header(title,desc)+f'<main id="contenuto"><div class="chapterhead"><p class="eyebrow">Starlink · Capitolo {i+1:02} di {len(chapters)}</p><h1>{escape(title)}</h1><p class="lead">{escape(desc)}</p><p class="readingtime">{max(1,round(words/190))} minuti di lettura · Edizione 10 ottobre 2026</p></div><div class="booklayout"><aside class="bookaside"><details open><summary>Capitoli</summary>{toc(slug)}</details></aside><article class="reading">{body}<nav class="chapterlinks" aria-label="Capitoli adiacenti">'+''.join(links)+'<a class="button" href="index.html">Indice del libro</a></nav></article></div></main>'+end()
 (BOOK/f'{slug}.html').write_text(page,encoding='utf-8')
intro=(BOOK/'contenuti'/'indice.html').read_text(encoding='utf-8')
total_it=f'{total:,}'.replace(',','.')
(BOOK/'index.html').write_text(header(data['titolo'],'Un libro sulla storia completa, la tecnologia, V3, OneWeb e i problemi delle megacostellazioni.')+f'<main id="contenuto"><div class="chapterhead cover"><p class="eyebrow">Programmi e monografie · SpaceX</p><h1>Starlink</h1><p class="lead">Costruire una rete, cambiare il cielo</p><p class="readingtime">{len(chapters)} capitoli · {total_it} parole, comprese fonti e didascalie · 10 ottobre 2026</p></div><div class="indexbody">{intro}<h2>Il percorso di lettura</h2>{toc()}</div></main>'+end(),encoding='utf-8')
credits=(BOOK/'contenuti'/'crediti.html').read_text(encoding='utf-8')
(BOOK/'crediti.html').write_text(header('Fonti e crediti','Licenze delle immagini, metodo, dichiarazioni e risultati verificati.')+'<main id="contenuto"><div class="chapterhead"><h1>Fonti e crediti</h1></div><article class="indexbody reading">'+credits+'</article></main>'+end(),encoding='utf-8')
css=(ROOT/'monografie'/'crew-dragon'/'libro.css').read_text(encoding='utf-8')
css+='\n.cover{background:linear-gradient(90deg,#050607e8,#05060785),url("assets/terra-notte.jpg") center/cover}.bookaside{max-height:90vh;overflow:auto}.status{display:inline-block;padding:5px 9px;border:1px solid #49606f;color:var(--amber);font-size:13px}.calculator{padding:24px;border:1px solid var(--line);background:#101b24}.calculator label{display:block;margin:15px 0}.calculator input{max-width:100%;width:100%;accent-color:var(--cyan)}.calculator output{display:block;font-size:23px;line-height:1.7;color:var(--amber)}.reading code{overflow-wrap:anywhere}@media(max-width:950px){.bookaside{max-height:none}}\n'
(BOOK/'libro.css').write_text(css,encoding='utf-8')
print(f'Capitoli: {sum((BOOK/"contenuti"/f"{c[0]}.html").exists() for c in chapters)}/{len(chapters)}; parole: {total}')
