"""Genera soltanto la monografia Artemis da contenuti e registri locali."""
from pathlib import Path
from html import escape
import json,re
ROOT=Path(__file__).resolve().parents[1];BOOK=ROOT/'monografie/artemis';data=json.loads((BOOK/'libro.json').read_text(encoding='utf-8'));chapters=data['capitoli'];sources=json.loads((BOOK/'fonti.json').read_text(encoding='utf-8'))
def toc(current=None):
 return '<ol class="toc">'+''.join(f'<li><a href="{s}.html"'+(' aria-current="page"' if current==s else '')+f'><span class="number">{i:02}</span>{escape(t)}</a></li>' for i,(s,t,d) in enumerate(chapters,1) if (BOOK/'contenuti'/f'{s}.html').exists())+'</ol>'
def head(title,desc):
 return f'<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} | Rivoluzione Spaziale</title><meta name="description" content="{escape(desc,quote=True)}"><link rel="stylesheet" href="libro.css"><script src="libro.js" defer></script></head><body><a class="skip" href="#contenuto">Vai al testo</a><header class="bookbar"><a class="brand" href="../../index.html">Rivoluzione <span>Spaziale</span></a><nav><a href="../../sezioni/monografie-spacex.html">Monografie</a><a href="index.html">Indice del libro</a></nav></header>'
def end():return '<footer>Rivoluzione Spaziale · Artemis · Edizione 10 ottobre 2026.<br>Pubblicazione indipendente · <a href="crediti.html">Fonti e licenze</a> · <a href="index.html">Indice</a></footer></body></html>'
def expand(body):
 def ref(m):return '<section class="sources"><h2>Fonti pubbliche e tracce</h2><ul>'+''.join(f'<li><a href="{escape(sources[k][1],quote=True)}">{escape(sources[k][0])}</a>. {escape(sources[k][2])}</li>' for k in m[1].split())+'</ul></section>'
 body=re.sub(r'<!-- FONTI:([^>]+) -->',ref,body)
 def photo(m):
  r=next(i for i in images if i['id']==m[1]);return f'<figure><img src="assets/{r["file"]}" alt="{escape(r["alt"],quote=True)}" loading="lazy"><figcaption>{escape(r["didascalia"])} · {escape(r["credito"])} · <a href="{escape(r["fonte"],quote=True)}">Fonte</a> · <a href="https://www.nasa.gov/nasa-brand-center/images-and-media/">Condizioni NASA</a>.</figcaption></figure>'
 return re.sub(r'<!-- FOTO:(\w+) -->',photo,body)
images=json.loads((BOOK/'immagini.json').read_text(encoding='utf-8')) if (BOOK/'immagini.json').exists() else [];total=0
for i,(s,t,d) in enumerate(chapters):
 p=BOOK/'contenuti'/f'{s}.html'
 if not p.exists():continue
 body=expand(p.read_text(encoding='utf-8'));words=len(re.findall(r'\b[\wÀ-ÿ’]+\b',re.sub('<[^>]+>',' ',body)));total+=words
 links=''.join(f'<a class="button" rel="{rel}" href="{chapters[j][0]}.html">{escape(chapters[j][1])}</a>' for rel,j in [('prev',i-1),('next',i+1)] if 0<=j<len(chapters) and (BOOK/'contenuti'/f'{chapters[j][0]}.html').exists())
 page=head(t,d)+f'<main id="contenuto"><div class="chapterhead"><p class="eyebrow">Artemis · Capitolo {i+1:02} di {len(chapters)}</p><h1>{escape(t)}</h1><p class="lead">{escape(d)}</p><p class="readingtime">{max(1,round(words/190))} minuti · Edizione 10 ottobre 2026</p></div><div class="booklayout"><aside class="bookaside"><details open><summary>Capitoli</summary>{toc(s)}</details></aside><article class="reading">{body}<nav class="chapterlinks">{links}<a class="button" href="index.html">Indice</a></nav></article></div></main>'+end();(BOOK/f'{s}.html').write_text(page,encoding='utf-8')
count=f'{total:,}'.replace(',','.');intro=(BOOK/'contenuti/indice.html').read_text(encoding='utf-8');(BOOK/'index.html').write_text(head(data['titolo'],'Storia e architettura Artemis: SLS, Orion, lander, scienza e base lunare.')+f'<main id="contenuto"><div class="chapterhead cover"><p class="eyebrow">Programmi e monografie</p><h1>Artemis</h1><p class="lead">Tornare sulla Luna, costruire una presenza</p><p class="readingtime">{len(chapters)} capitoli · {count} parole con fonti e didascalie · 10 ottobre 2026</p></div><article class="indexbody">{intro}<h2>Il percorso di lettura</h2>{toc()}</article></main>'+end(),encoding='utf-8')
p=BOOK/'contenuti/crediti.html'
if p.exists():
 listing='<ul>'+''.join(f'<li><a href="assets/{r["file"]}">{r["file"]}</a> · {escape(r["credito"])} · <a href="{escape(r["fonte"],quote=True)}">Fonte</a>. {escape(r["didascalia"])} {escape(r["modifiche"])}</li>' for r in images)+'</ul>'
 (BOOK/'crediti.html').write_text(head('Fonti e licenze','Crediti delle fotografie NASA e degli schemi originali.')+'<main id="contenuto"><div class="chapterhead"><h1>Fonti e licenze</h1></div><article class="reading indexbody">'+p.read_text(encoding='utf-8').replace('<!-- CREDITI -->',listing)+'</article></main>'+end(),encoding='utf-8')
css=(ROOT/'monografie/crew-dragon/libro.css').read_text(encoding='utf-8');css+='\n.cover{background:linear-gradient(90deg,#050607e8,#05060765),url("assets/artemis2-lancio.jpg") center/cover}.bookaside{max-height:90vh;overflow:auto}.reading dt{color:var(--amber);font-weight:bold;margin-top:20px}.reading dd{margin:8px 0 20px;line-height:1.8}.filters input{max-width:100%}@media(max-width:950px){.bookaside{max-height:none}}\n';(BOOK/'libro.css').write_text(css,encoding='utf-8');print('Capitoli',sum((BOOK/'contenuti'/f'{s}.html').exists() for s,t,d in chapters),'parole',total)
