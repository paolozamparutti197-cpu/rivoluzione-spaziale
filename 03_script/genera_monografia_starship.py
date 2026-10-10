"""Costruisce soltanto il libro Starship, a partire dai frammenti salvati."""
from pathlib import Path
from html import escape
import json,re,csv
ROOT=Path(__file__).resolve().parents[1]; BOOK=ROOT/'monografie/starship'
data=json.loads((BOOK/'libro.json').read_text(encoding='utf-8'));chapters=data['capitoli']
sources=json.loads((BOOK/'fonti.json').read_text(encoding='utf-8'))
for n in range(1,15):
 key=f'flight{n}';sources[key]=[f'SpaceX, resoconto Flight {n}',f'https://www.spacex.com/launches/starship-flight-{n}','Resoconto del costruttore; obiettivi di prova distinti dal successo commerciale.']
sources['flight1']=['FAA, primo test integrato e chiusura dell’indagine','https://www.faa.gov/newsroom/faa-closes-spacex-starship-mishap-investigation','Primo volo del 20 aprile 2023 e azioni correttive richieste.']
(BOOK/'fonti-complete.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
flights=json.loads((BOOK/'voli.json').read_text(encoding='utf-8'))
with (BOOK/'voli.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=flights[0].keys());writer.writeheader();writer.writerows(flights)
def registry():
 rows=''
 for r in flights:
  n=r['numero'];rows+='<tr>'+''.join('<td>'+escape(str(r[k]))+'</td>' for k in ['numero','data','versione','profilo','booster','ship','carico'])+f'<td>{escape(r["nota"])}<small><a href="{escape(sources[f"flight{n}"][1],quote=True)}">Fonte del volo</a></small></td></tr>'
 return '<div class="table-wrap"><table id="voli"><caption>Voli integrati · dati al 10 ottobre 2026</caption><thead><tr>'+''.join('<th scope="col">'+x+'</th>' for x in ['Volo','Data','Configurazione','Traiettoria','Super Heavy','Ship','Carico','Nota e fonte'])+'</tr></thead><tbody>'+rows+'</tbody></table></div>'
def toc(current=None):
 return '<ol class="toc">'+''.join(f'<li><a href="{slug}.html"'+(' aria-current="page"' if current==slug else '')+f'><span class="number">{i:02}</span>{escape(title)}</a></li>' for i,(slug,title,desc) in enumerate(chapters,1) if (BOOK/'contenuti'/f'{slug}.html').exists())+'</ol>'
def header(title,desc):
 return f'<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} | Rivoluzione Spaziale</title><meta name="description" content="{escape(desc,quote=True)}"><link rel="stylesheet" href="libro.css"><script src="libro.js" defer></script></head><body><a class="skip" href="#contenuto">Vai al testo</a><header class="bookbar"><a class="brand" href="../../index.html">Rivoluzione <span>Spaziale</span></a><nav aria-label="Navigazione principale"><a href="../../sezioni/spacex.html">SpaceX</a><a href="../../sezioni/monografie-spacex.html">Monografie</a><a href="index.html">Indice del libro</a></nav></header>'
def end():return '<footer>Rivoluzione Spaziale · Monografia Starship · Edizione 10 ottobre 2026.<br>Pubblicazione indipendente. <a href="crediti.html">Fonti, immagini e criteri</a> · <a href="index.html">Indice</a></footer></body></html>'
def references(body):
 def replace(m):return '<section class="sources"><h2>Fonti pubbliche e tracce</h2><ul>'+''.join(f'<li><a href="{escape(sources[k][1],quote=True)}">{escape(sources[k][0])}</a>. {escape(sources[k][2])}</li>' for k in m[1].split())+'</ul></section>'
 return re.sub(r'<!-- FONTI:([^>]+) -->',replace,body)
total=0
for i,(slug,title,desc) in enumerate(chapters):
 source=BOOK/'contenuti'/f'{slug}.html'
 if not source.exists():continue
 body=references(source.read_text(encoding='utf-8')).replace('<!-- REGISTRO_VOLI -->',registry())
 words=len(re.findall(r'\b[\wÀ-ÿ’]+\b',re.sub('<[^>]+>',' ',body)));total+=words
 links=''.join(f'<a class="button" rel="{rel}" href="{chapters[j][0]}.html">{escape(chapters[j][1])}</a>' for rel,j in [('prev',i-1),('next',i+1)] if 0<=j<len(chapters) and (BOOK/'contenuti'/f'{chapters[j][0]}.html').exists())
 page=header(title,desc)+f'<main id="contenuto"><div class="chapterhead"><p class="eyebrow">Starship · Capitolo {i+1:02} di {len(chapters)}</p><h1>{escape(title)}</h1><p class="lead">{escape(desc)}</p><p class="readingtime">{max(1,round(words/190))} minuti · Edizione 10 ottobre 2026</p></div><div class="booklayout"><aside class="bookaside"><details open><summary>Capitoli</summary>{toc(slug)}</details></aside><article class="reading">{body}<nav class="chapterlinks" aria-label="Capitoli adiacenti">{links}<a class="button" href="index.html">Indice</a></nav></article></div></main>'+end()
 (BOOK/f'{slug}.html').write_text(page,encoding='utf-8')
intro=(BOOK/'contenuti/indice.html').read_text(encoding='utf-8');count=f'{total:,}'.replace(',','.')
(BOOK/'index.html').write_text(header(data['titolo'],'Un libro sullo sviluppo Starship: Red Dragon, Raptor, Starbase, voli, riuso, Luna e Marte.')+f'<main id="contenuto"><div class="chapterhead cover"><p class="eyebrow">Programmi e monografie · SpaceX</p><h1>Starship</h1><p class="lead">Storia di un’idea, costruzione di un sistema</p><p class="readingtime">{len(chapters)} capitoli · {count} parole con fonti e didascalie · Edizione 10 ottobre 2026</p></div><div class="indexbody">{intro}<h2>Il percorso di lettura</h2>{toc()}</div></main>'+end(),encoding='utf-8')
credit=BOOK/'contenuti/crediti.html'
if credit.exists():
 images=json.loads((BOOK/'immagini.json').read_text(encoding='utf-8'))
 licenses={'CC BY 2.0':'https://creativecommons.org/licenses/by/2.0/','CC BY-SA 2.0':'https://creativecommons.org/licenses/by-sa/2.0/','CC BY-SA 4.0':'https://creativecommons.org/licenses/by-sa/4.0/','CC0 storico documentato':'https://creativecommons.org/publicdomain/zero/1.0/','Materiale NASA per uso informativo; condizioni NASA':'https://www.nasa.gov/nasa-brand-center/images-and-media/'}
 listing='<ul>'+''.join(f'<li><a href="assets/{r["file"]}">{escape(r["file"])}</a> · {escape(r["autore"])} · <a href="{licenses[r["licenza"]]}">{escape(r["licenza"])}</a> · <a href="{escape(r["fonte"],quote=True)}">Fonte e attribuzione</a>. {escape(r["modifiche"])}</li>' for r in images)+'</ul>'
 body=credit.read_text(encoding='utf-8').replace('<!-- CREDITI_IMMAGINI -->',listing)
 (BOOK/'crediti.html').write_text(header('Fonti e crediti','Materiali documentari, grafici originali e licenze.')+'<main id="contenuto"><div class="chapterhead"><h1>Fonti e crediti</h1></div><article class="indexbody reading">'+body+'</article></main>'+end(),encoding='utf-8')
css=(ROOT/'monografie/crew-dragon/libro.css').read_text(encoding='utf-8')
css+='\n.cover{background:linear-gradient(90deg,#050607e8,#05060775),url("assets/ift5-ignition.jpg") center/cover}.bookaside{max-height:90vh;overflow:auto}.diagram-light{background:white}.calculator{padding:24px;border:1px solid var(--line);background:#101b24}.calculator input{width:100%;accent-color:var(--cyan)}.calculator output{display:block;color:var(--amber);font-size:23px}.map{height:550px;background:#12222b}.map .leaflet-popup-content{color:#172633}.map .leaflet-control a{color:#111}.map-list{display:grid;grid-template-columns:1fr 1fr;gap:12px}.reading dt{color:var(--amber);font-weight:bold;margin-top:20px}.reading dd{margin:8px 0 20px;font-size:17px;line-height:1.7}@media(max-width:950px){.bookaside{max-height:none}}@media(max-width:550px){.map-list{grid-template-columns:1fr}.map{height:450px}}\n'
(BOOK/'libro.css').write_text(css,encoding='utf-8');print('Capitoli',sum((BOOK/'contenuti'/f'{c[0]}.html').exists() for c in chapters),'/',len(chapters),'parole',total)
