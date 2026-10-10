"""Genera esclusivamente Starmind da testi HTML e registri locali."""
from pathlib import Path
from html import escape
import json,re,csv
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'monografie/starmind'
data=json.loads((B/'libro.json').read_text(encoding='utf8'));chapters=data['capitoli'];sources=json.loads((B/'fonti.json').read_text(encoding='utf8'));images=json.loads((B/'immagini.json').read_text(encoding='utf8'));diagrams=json.loads((B/'schemi.json').read_text(encoding='utf8'));events=json.loads((B/'cronologia.json').read_text(encoding='utf8'))
def toc(current=None):
 return '<ol class="toc">'+''.join(f'<li><a href="{s}.html"'+(' aria-current="page"' if current==s else '')+f'><span class="number">{i:02}</span>{escape(t)}</a></li>' for i,(s,t,d) in enumerate(chapters,1))+'</ol>'
def head(title,desc):
 return f'<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} | Rivoluzione Spaziale</title><meta name="description" content="{escape(desc,quote=True)}"><link rel="stylesheet" href="libro.css"><script src="libro.js" defer></script></head><body><a class="skip" href="#contenuto">Vai al testo</a><header class="bookbar"><a class="brand" href="../../index.html">Rivoluzione <span>Spaziale</span></a><nav aria-label="Navigazione principale"><a href="../../sezioni/spacex.html">SpaceX</a><a href="../../sezioni/monografie-spacex.html">Monografie</a><a href="index.html">Indice del libro</a></nav></header>'
def end():return '<footer>Rivoluzione Spaziale · Starmind · Edizione 10 ottobre 2026.<br>Pubblicazione indipendente · <a href="crediti.html">Fonti, immagini e criteri</a> · <a href="index.html">Indice del libro</a></footer></body></html>'
def refs(keys):
 return '<section class="sources"><h2>Fonti pubbliche e tracce</h2><ul>'+''.join(f'<li><a href="{escape(sources[k][1],quote=True)}">{escape(sources[k][0])}</a>. {escape(sources[k][2])}</li>' for k in keys)+'</ul></section>'
def chronology():
 types=sorted({x['tipo'] for x in events});rows=''.join(f'<tr data-tipo="{escape(e["tipo"])}"><td>{escape(e["data"])}</td><td>{escape(e["evento"])}</td><td>{escape(e["tipo"])}</td><td>{escape(e["stato"])}</td><td><a href="{escape(sources[e["fonte"]][1],quote=True)}">Fonte</a></td></tr>' for e in events)
 options=''.join(f'<option>{escape(t)}</option>' for t in types)
 return '<div class="filters"><label>Cerca nella cronologia<input id="cerca-cronologia" type="search" placeholder="Evento, data o programma"></label><label>Tipo di evento<select id="tipo-cronologia"><option value="">Tutti</option>'+options+'</select></label><button type="button" id="reset-cronologia">Ripristina</button></div><p id="risultati" class="note" aria-live="polite">'+str(len(events))+' eventi visualizzati</p><p id="nessun-evento" class="callout" hidden>Nessun evento corrisponde alla ricerca.</p><div class="table-wrap"><table id="cronologia"><caption>Precedenti e sviluppo del calcolo orbitale</caption><thead><tr><th>Data</th><th>Evento</th><th>Tipo</th><th>Stato e significato</th><th>Traccia</th></tr></thead><tbody>'+rows+'</tbody></table></div><p class="note"><a href="cronologia.csv" download>Scarica CSV</a> · <a href="cronologia.json">Registro JSON</a></p>'
def expand(body):
 body=re.sub(r'<!-- FONTI:\s*([^>]+?)\s*-->',lambda m:refs(m[1].split()),body)
 def photo(m):
  r=next(i for i in images if i['id']==m[1]);return f'<figure><a class="image-link" href="assets/{r["file"]}" aria-label="Apri fotografia: {escape(r["alt"],quote=True)}"><img src="assets/{r["file"]}" alt="{escape(r["alt"],quote=True)}" loading="lazy" decoding="async"></a><figcaption>{escape(r["didascalia"])} · {escape(r["credito"])} · <a href="{escape(r["fonte"],quote=True)}">Fonte</a> · <a href="{escape(r["licenza_url"],quote=True)}">{escape(r["licenza"])}</a>.</figcaption></figure>'
 body=re.sub(r'<!-- FOTO:([\w-]+) -->',photo,body)
 def diagram(m):
  r=next(x for x in diagrams if x['file']==m[1]+'.svg');return f'<figure class="svgfigure"><a class="image-link" href="assets/{r["file"]}" aria-label="Apri schema: {escape(r["titolo"],quote=True)}"><img src="assets/{r["file"]}" alt="{escape(r["descrizione"],quote=True)}" loading="lazy"></a><figcaption>{escape(r["descrizione"])} Schema originale Rivoluzione Spaziale, CC BY 4.0. <a href="assets/{r["file"]}">Apri a piena dimensione</a>.</figcaption></figure>'
 body=re.sub(r'<!-- SCHEMA:([\w-]+) -->',diagram,body)
 return body.replace('<!-- CRONOLOGIA -->',chronology())
total=0;figures=0
for i,(slug,title,desc) in enumerate(chapters):
 p=B/'contenuti'/f'{slug}.html'
 if not p.exists():raise FileNotFoundError(p)
 body=expand(p.read_text(encoding='utf8'));words=len(re.findall(r'\b[\wÀ-ÿ’]+\b',re.sub('<[^>]+>',' ',body)));total+=words;figures+=body.count('<figure')
 links=''.join(f'<a class="button" rel="{rel}" href="{chapters[j][0]}.html">{escape(chapters[j][1])}</a>' for rel,j in [('prev',i-1),('next',i+1)] if 0<=j<len(chapters))
 page=head(title,desc)+f'<main id="contenuto"><div class="chapterhead"><p class="eyebrow">Starmind · Capitolo {i+1:02} di {len(chapters)}</p><h1>{escape(title)}</h1><p class="lead">{escape(desc)}</p><p class="readingtime">{max(1,round(words/190))} minuti di lettura · Edizione 10 ottobre 2026</p></div><div class="booklayout"><aside class="bookaside"><details open><summary>Capitoli</summary>{toc(slug)}</details></aside><article class="reading">{body}<nav class="chapterlinks" aria-label="Capitoli adiacenti">{links}<a class="button" href="index.html">Indice del libro</a></nav></article></div></main>'+end()
 (B/f'{slug}.html').write_text(page,encoding='utf8')
count=f'{total:,}'.replace(',','.');intro=expand((B/'contenuti/indice.html').read_text(encoding='utf8'))
(B/'index.html').write_text(head(data['titolo'],'Il progetto Starmind, AI1 e i data center orbitali: storia, energia, calore, reti e industria.')+f'<main id="contenuto"><div class="chapterhead cover"><p class="eyebrow">Programmi e monografie</p><h1>Starmind</h1><p class="lead">Portare il calcolo nello spazio</p><p class="readingtime">{len(chapters)} capitoli · {count} parole con fonti e didascalie · 10 ottobre 2026</p></div><article class="indexbody">{intro}<h2>Il percorso di lettura</h2>{toc()}</article></main>'+end(),encoding='utf8')
listing='<ul>'+''.join(f'<li><a href="assets/{r["file"]}">{escape(r["file"])}</a> · {escape(r["credito"])} · <a href="{escape(r["fonte"],quote=True)}">Fonte</a> · <a href="{escape(r["licenza_url"],quote=True)}">{escape(r["licenza"])}</a>. {escape(r["didascalia"])} {escape(r["modifiche"])}</li>' for r in images)+'</ul>'
credit=(B/'contenuti/crediti.html').read_text(encoding='utf8').replace('<!-- CREDITI -->',listing).replace('<!-- TUTTEFONTI -->',refs(sources))
(B/'crediti.html').write_text(head('Fonti, immagini e criteri','Crediti delle fotografie documentarie e degli schemi originali del libro Starmind.')+'<main id="contenuto"><div class="chapterhead"><h1>Fonti, immagini e criteri</h1></div><article class="reading indexbody">'+credit+'</article></main>'+end(),encoding='utf8')
css=(ROOT/'monografie/crew-dragon/libro.css').read_text(encoding='utf8')
css+='''
.cover{background:linear-gradient(90deg,#050607ed,#05060775),url("assets/solari-iss.jpg") center/cover}.bookaside{max-height:90vh;overflow:auto}.reading dt{color:var(--amber);font-weight:700;margin-top:24px}.reading dd{margin:10px 0 24px;line-height:1.8;font-size:17px;color:#dce2e7}.image-link{display:block}.svgfigure img{max-height:none}caption{padding:15px;text-align:left;color:var(--muted);font-size:14px;line-height:1.6;background:#101b24}.lab{border:1px solid #315469;background:#0e1821;padding:24px;border-radius:7px;margin:35px 0;scroll-margin-top:20px}.lab h3{margin-top:0}.lab-fields{display:grid;grid-template-columns:1fr 1fr;gap:18px}.lab label{display:flex;flex-direction:column;gap:10px;font-size:15px;line-height:1.5}.lab input{width:100%;min-width:0;background:#070d12;color:#fff;border:1px solid #49606f;padding:12px;font:inherit}.lab output{display:block;padding:22px 0;font-size:18px;line-height:1.75;color:var(--cyan)}button{background:#142b3c;color:#fff;border:1px solid #49606f;border-radius:4px;padding:12px 16px;font:inherit;cursor:pointer}.filters button{align-self:end}.filters input,.filters select{max-width:100%;min-width:0}.filters label{max-width:100%}[hidden]{display:none!important}.note{overflow-wrap:anywhere}.sources a,figcaption a,.reading li a{overflow-wrap:anywhere}#cronologia{scroll-margin-top:20px}@media(max-width:950px){.bookaside{max-height:none}}@media(max-width:550px){.lab-fields{grid-template-columns:1fr}.lab{padding:18px}.lab output{font-size:17px}.filters{padding:16px}}
'''
(B/'libro.css').write_text(css,encoding='utf8')
with (B/'cronologia.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=['data','evento','tipo','stato','fonte']);w.writeheader();w.writerows([{**e,'fonte':sources[e['fonte']][1]} for e in events])
print(json.dumps(dict(capitoli=len(chapters),parole=total,figure_capitoli=figures,fotografie=len(images),schemi=len(diagrams),eventi=len(events)),ensure_ascii=False))
