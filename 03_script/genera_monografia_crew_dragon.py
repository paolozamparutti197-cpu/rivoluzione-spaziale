"""Costruisce gli HTML della monografia da frammenti editoriali versionati.

Non rigenera il resto del sito e non modifica dati operativi o documenti utente.
"""
from pathlib import Path
from html import escape
import json
import re
import csv
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / 'monografie' / 'crew-dragon'
DATA = json.loads((BOOK / 'libro.json').read_text(encoding='utf-8'))
CHAPTERS = DATA['capitoli']

def registry():
    data=json.loads((BOOK/'voli.json').read_text(encoding='utf-8'))
    missions=sorted(data['missioni'],key=lambda m:m['lancio'])
    human=[m for m in missions if m['equipaggio']]
    seats=sum(len(m['equipaggio']) for m in human)
    assert len({m['nome'] for m in missions})==len(missions)
    for m in missions:
        assert date.fromisoformat(m['lancio'])<=date.fromisoformat(data['aggiornato'])
        assert not m['rientro'] or date.fromisoformat(m['lancio'])<date.fromisoformat(m['rientro'])<=date.fromisoformat(data['aggiornato'])
    cards=f'<div class="metrics"><div class="metric"><strong>{len(missions)}</strong>voli orbitali, incluso Demo-1 senza equipaggio</div><div class="metric"><strong>{len(human)}</strong>missioni orbitali con persone</div><div class="metric"><strong>{seats}</strong>posti occupati al lancio; non persone uniche</div></div>'
    controls='''<div class="filters"><label for="cerca-voli">Cerca missione, persona o capsula<input id="cerca-voli" type="search" placeholder="Es. Cristoforetti, Freedom, Ax-3"></label><label for="tipo-volo">Categoria<select id="tipo-volo"><option value="tutti">Tutte le missioni</option><option value="nasa">NASA, incluso Demo-2</option><option value="privata">Missioni private</option><option value="test">Test senza equipaggio</option></select></label></div><p id="risultati" class="note" aria-live="polite">22 missioni visualizzate. Il registro funziona anche senza JavaScript.</p>'''
    rows=[]
    csvrows=[]
    for m in missions:
        crew='<br>'.join(escape(p) for p in m['equipaggio']) or 'Nessuna persona'
        if 'ritorno' in m:crew+='<small>Al ritorno: '+escape(', '.join(m['ritorno']))+'</small>'
        returned=m['rientro'] or 'In corso'
        row=f'<tr data-tipo="{m["tipo"]}"><th scope="row">{escape(m["nome"])}</th><td><time datetime="{m["lancio"]}">{m["lancio"]}</time><small>Rientro: {returned}</small></td><td>{escape(m["capsula"])}<small>{escape(m["destinazione"])}</small></td><td>{crew}</td><td>{escape(m["nota"])}<small><a href="{m["fonte"]}">Fonte primaria</a>'
        if m.get('fonte_rientro'):row+=f' · <a href="{m["fonte_rientro"]}">Rientro documentato</a>'
        rows.append(row+'</small></td></tr>')
        csvrows.append([m['nome'],m['tipo'],m['lancio'],m['rientro'] or '',m['capsula'],m['destinazione'],'; '.join(m['equipaggio']),'; '.join(m.get('ritorno',m['equipaggio'])),m['nota'],m['fonte'],m.get('fonte_rientro','')])
    with (BOOK/'registro-voli.csv').open('w',encoding='utf-8-sig',newline='') as output:
        writer=csv.writer(output)
        writer.writerow(['Missione','Categoria','Lancio_UTC','Rientro_UTC','Capsula','Destinazione','Equipaggio_lancio','Equipaggio_rientro','Nota','Fonte','Fonte_rientro'])
        writer.writerows(csvrows)
    return cards+controls+'<div class="table-wrap" tabindex="0" role="region" aria-label="Registro completo scorrevole"><table id="registro"><caption>Voli orbitali Crew Dragon · Date UTC · Controllo al 9 ottobre 2026</caption><thead><tr><th scope="col">Missione</th><th scope="col">Lancio e ritorno UTC</th><th scope="col">Capsula e destinazione</th><th scope="col">Equipaggio al lancio</th><th scope="col">Note e fonti</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div><p class="note"><a href="registro-voli.csv" download>Scarica il registro CSV</a> · <a href="voli.json">Dati strutturati JSON</a></p>'

def header(title, description):
    return f'''<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} | Rivoluzione Spaziale</title><meta name="description" content="{escape(description, quote=True)}">
<link rel="stylesheet" href="libro.css"><script src="libro.js" defer></script></head><body>
<a class="skip" href="#contenuto">Vai al testo</a>
<header class="bookbar"><a class="brand" href="../../index.html">Rivoluzione <span>Spaziale</span></a>
<nav aria-label="Navigazione principale"><a href="../../sezioni/spacex.html">SpaceX</a><a href="../../sezioni/storia-spacex.html">Storia</a><a href="index.html">Indice del libro</a></nav></header>
'''

def end():
    return '''<footer>Rivoluzione Spaziale · Monografia Crew Dragon · Edizione del 9 ottobre 2026.<br>
Racconto indipendente, non una pubblicazione NASA o SpaceX. Schemi divulgativi, non istruzioni operative.<br>
<a href="crediti.html">Fonti, immagini e criteri editoriali</a> · <a href="index.html">Indice completo</a></footer></body></html>'''

def contents(current=None):
    items = []
    for i, (slug, title, desc) in enumerate(CHAPTERS, 1):
        present = (BOOK / 'contenuti' / (slug + '.html')).exists()
        label = f'<span class="number">{i:02}</span>{escape(title)}'
        items.append(f'<li><a {"aria-current=\"page\"" if current == slug else ""} href="{slug}.html">{label}</a></li>' if present else f'<li class="pending">{label} <small>In lavorazione</small></li>')
    return '<ol class="toc">' + ''.join(items) + '</ol>'

total = 0
for i, (slug, title, desc) in enumerate(CHAPTERS):
    source = BOOK / 'contenuti' / (slug + '.html')
    if not source.exists():
        continue
    body = source.read_text(encoding='utf-8')
    if '<!-- REGISTRO -->' in body:
        body=body.replace('<!-- REGISTRO -->',registry())
    words = len(re.findall(r"\b[\wÀ-ÿ’]+\b", re.sub('<[^>]+>', ' ', body)))
    total += words
    neighbors = []
    if i and (BOOK / 'contenuti' / (CHAPTERS[i-1][0] + '.html')).exists():
        neighbors.append(f'<a class="button" rel="prev" href="{CHAPTERS[i-1][0]}.html">← {escape(CHAPTERS[i-1][1])}</a>')
    neighbors.append('<a class="button" href="index.html">Indice del libro</a>')
    if i + 1 < len(CHAPTERS) and (BOOK / 'contenuti' / (CHAPTERS[i+1][0] + '.html')).exists():
        neighbors.append(f'<a class="button" rel="next" href="{CHAPTERS[i+1][0]}.html">{escape(CHAPTERS[i+1][1])} →</a>')
    page = header(title, desc) + f'''<main id="contenuto"><div class="chapterhead"><p class="eyebrow">Crew Dragon · Capitolo {i+1:02} di 12</p><h1>{escape(title)}</h1><p class="lead">{escape(desc)}</p><p class="readingtime">{max(1, round(words/190))} minuti di lettura · Edizione 9 ottobre 2026</p></div>
<div class="booklayout"><aside class="bookaside"><details open><summary>Capitoli</summary>{contents(slug)}</details></aside><article class="reading">{body}<nav class="chapterlinks" aria-label="Capitoli adiacenti">{''.join(neighbors)}</nav></article></div></main>''' + end()
    (BOOK / (slug + '.html')).write_text(page, encoding='utf-8')

index_body = (BOOK / 'contenuti' / 'indice.html').read_text(encoding='utf-8') if (BOOK / 'contenuti' / 'indice.html').exists() else '<p>Il libro è in costruzione. I capitoli completati vengono salvati durante il lavoro.</p>'
(BOOK / 'index.html').write_text(header(DATA['titolo'], 'Un libro in dodici capitoli sulla storia, lo sviluppo e le missioni di Crew Dragon.') + f'<main id="contenuto"><div class="chapterhead cover"><p class="eyebrow">Programmi e monografie · SpaceX</p><h1>Crew Dragon</h1><p class="lead">Costruire la fiducia, portare le persone nello spazio</p><p class="readingtime">Dodici capitoli · {total:,} parole negli HTML · Edizione 9 ottobre 2026</p></div><div class="indexbody">{index_body}<h2>Il percorso di lettura</h2>{contents()}<p class="note">Il registro distingue i voli orbitali dalle prove suborbitali, le persone lanciate da quelle riportate a Terra e i risultati dalle previsioni.</p></div></main>' + end(), encoding='utf-8')
print(f'HTML salvati: {sum((BOOK / "contenuti" / (c[0]+".html")).exists() for c in CHAPTERS)}/12; parole incluse fonti e didascalie: {total}')
