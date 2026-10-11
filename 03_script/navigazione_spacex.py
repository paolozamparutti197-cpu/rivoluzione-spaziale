"""Navigazione e indice full-text, senza dipendenze o accessi alla rete.

Eseguire dopo un aggiornamento di HTML: python 03_script/navigazione_spacex.py.
Le trasformazioni sono idempotenti e non modificano testi, dati o workbook.
"""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, quote
import argparse, json, re, os

ROOT = Path(__file__).resolve().parents[1]
VERSION = '20261011-lettori'
SECTIONS = ['spacex','storia-spacex','monografie-spacex','storico-lanci','lanci-imminenti','starship','lancio13','lancio14','pad-di-lancio','localita-spacex','guida-lancio-slc40']
TOPICS = [('Starship',r'starship|super heavy|raptor|boca chica|red dragon'),('Falcon',r'falcon|merlin|crs.?7|amos.?6'),('Crew Dragon',r'crew dragon|commercial crew|demo.?2|ax.?[1-9]'),('Starlink',r'starlink|oneweb|megacostell'),('Artemis',r'artemis|orion|blue moon|gateway'),('AI nello spazio',r'starmind|data center|intelligenza artificiale|xai'),('Infrastrutture',r'starbase|vandenberg|slc.?40|lc.?39|piazzol')]

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.block=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','nav','aside','footer'): self.block+=1
        if tag in ('p','h1','h2','h3','li','tr','br'): self.parts.append(' ')
    def handle_endtag(self, tag):
        if tag in ('script','style','nav','aside','footer'): self.block=max(0,self.block-1)
        if tag in ('p','h1','h2','h3','li','tr'): self.parts.append(' ')
    def handle_data(self, data):
        if not self.block: self.parts.append(data)
    def text(self): return re.sub(r'\s+',' ',' '.join(self.parts)).strip()

def plain(html):
    parser=Text(); parser.feed(html); return parser.text()

def relative(path, target): return quote(os.path.relpath(ROOT/target,path.parent).replace('\\','/'),safe='/')

def title(html):
    found=re.search(r'<h1\b[^>]*>(.*?)</h1>',html,re.S|re.I)
    if not found: found=re.search(r'<title\b[^>]*>(.*?)</title>',html,re.S|re.I)
    return plain(found.group(1)) if found else 'SpaceX'

def category(path):
    s=path.relative_to(ROOT).as_posix()
    if s.startswith('monografie/'): return 'Monografia'
    if '/missioni/' in s: return 'Missione'
    if '/veicoli/' in s: return 'Veicolo'
    if s.startswith('archivio/') or 'storico-lanci' in s: return 'Dati e metodo'
    if any(x in s for x in ['localita','pad-di-lancio','guida-lancio']): return 'Infrastrutture'
    if s.startswith('documenti per sito/'):
        return 'Storia' if path.name in history_files() else 'Notizia e dossier'
    return 'Indice e guida'

def history_files():
    p=ROOT/'sezioni/storia-spacex.html'
    return {Path(unquote(urlsplit(h).path)).name for h in re.findall(r'href="([^"]+)"',p.read_text(encoding='utf8')) if 'documenti' in h} if p.exists() else set()

def discover():
    paths={ROOT/'sezioni'/f'{s}.html' for s in SECTIONS}
    for folder in (ROOT/'monografie',ROOT/'archivio/spacex'):
        paths.update(p for p in folder.rglob('*.html') if 'contenuti' not in p.parts)
    # Solo articoli pubblici raggiunti dalle pagine SpaceX, mai copie in output/tmp.
    queue=list(paths)
    while queue:
        p=queue.pop()
        if not p.is_file(): continue
        for link in re.findall(r'href=["\']([^"\']+)',p.read_text(encoding='utf8')):
            u=urlsplit(link)
            if u.scheme or u.netloc: continue
            q=(p.parent/unquote(u.path)).resolve()
            if q.parent==ROOT/'documenti per sito' and q.suffix=='.html' and q not in paths:
                paths.add(q);queue.append(q)
    return sorted(p for p in paths if p.exists())

def decorate(path,html):
    if '<main' not in html or '</head>' not in html: return html
    html=re.sub(r'<!-- LETTORI:HEAD -->.*?<!-- /LETTORI:HEAD -->','',html,flags=re.S)
    html=re.sub(r'<!-- LETTORI:NAV -->.*?<!-- /LETTORI:NAV -->','',html,flags=re.S)
    css=relative(path,'css/lettori-spacex.css'); js=relative(path,'js/lettori-spacex.js')
    html=html.replace('</head>',f'<!-- LETTORI:HEAD --><link rel="stylesheet" href="{css}?v={VERSION}"><script src="{js}?v={VERSION}" defer></script><!-- /LETTORI:HEAD --></head>',1)
    def link(target,label): return f'<a href="{relative(path,target)}">{escape(label)}</a>'
    ancestors=[link('index.html','Home'),link('sezioni/spacex.html','SpaceX')]
    if path.parent.parent.name=='monografie':
        ancestors.append(link('sezioni/monografie-spacex.html','Monografie'))
        if path.name!='index.html': ancestors.append(link(f'monografie/{path.parent.name}/index.html',path.parent.name.replace('-',' ').title()))
    elif 'archivio' in path.parts: ancestors.append(link('archivio/spacex/index.html','Archivio lanci'))
    elif category(path)=='Storia': ancestors.append(link('sezioni/storia-spacex.html','Storia'))
    crumbs=' <span aria-hidden="true">›</span> '.join(ancestors)+f' <span aria-hidden="true">›</span> <span aria-current="page">{escape(title(html))}</span>'
    search=relative(path,'sezioni/cerca-spacex.html')
    contexts={
        'starship':[('monografie/starship/06-raptor-ciclo.html','Il ciclo Raptor'),('monografie/starship/20-rifornimento.html','Il rifornimento orbitale'),('monografie/artemis/13-starship-hls.html','Starship nel programma Artemis')],
        'starlink':[('monografie/starlink/16-oneweb.html','Il confronto OneWeb'),('monografie/starlink/19-cielo-astronomia.html','Il cielo e l’astronomia'),('monografie/starship/17-v3-orbita.html','Starship e i satelliti V3')],
        'crew-dragon':[('monografie/crew-dragon/06-incidente-2019.html','La sicurezza dopo l’incidente del 2019'),('archivio/spacex/elenco.html','Le missioni nel registro operativo')],
        'artemis':[('monografie/starship/20-rifornimento.html','La dipendenza dal rifornimento'),('monografie/artemis/11-artemis-iii.html','Il piano Artemis aggiornato')],
        'starmind':[('monografie/starlink/09-laser.html','Le reti laser'),('monografie/starship/19-riutilizzo.html','Il riutilizzo del lanciatore')],
        'archivio':[('sezioni/storico-lanci.html','Il riepilogo dei lanci'),('archivio/spacex/metodo.html','Come si contano lanci e recuperi')],
    }
    key=next((k for k in contexts if k in path.parts),None)
    if not key and path.name in ('starship.html','lancio13.html','lancio14.html'):key='starship'
    related=[link(target,label) for target,label in contexts.get(key,[]) if ROOT/target!=path and (ROOT/target).exists()]
    context='<details class="reader-context"><summary>Letture collegate</summary><ul>'+''.join(f'<li>{a}</li>' for a in related)+'</ul></details>' if related else ''
    nav=f'''<!-- LETTORI:NAV --><div class="reader-tools"><a class="reader-skip" href="#reader-content">Vai al contenuto</a><nav class="reader-breadcrumb" aria-label="Percorso della pagina">{crumbs}</nav><div class="reader-actions">{link('sezioni/percorsi-spacex.html','Da dove cominciare')} {link('sezioni/cerca-spacex.html','Cerca in SpaceX')}</div><form class="reader-quick" action="{search}" method="get" role="search" aria-label="Ricerca nella sezione SpaceX"><label>Cerca in capitoli, missioni e dossier<input name="q" type="search" placeholder="Es. Raptor, CRS-7, SX-0714" maxlength="180"></label><button type="submit">Cerca</button></form>{context}</div><span id="reader-content" tabindex="-1"></span><!-- /LETTORI:NAV -->'''
    return re.sub(r'(<main\b[^>]*>)',lambda m:m[1]+nav,html,count=1)

def page(title_,body):
    return f'<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title_)} | Rivoluzione Spaziale</title><link rel="stylesheet" href="../css/style.css?v=20260830-f13-f14"></head><body><header class="topbar"><a class="brand" href="../index.html">Rivoluzione <span>Spaziale</span></a><nav class="nav"><a href="spacex.html">SpaceX</a><a href="monografie-spacex.html">Monografie</a></nav></header><main><div class="reader-hub"><h1>{escape(title_)}</h1>{body}</div></main><footer class="footer">Rivoluzione Spaziale · Percorsi e ricerca SpaceX</footer></body></html>'

def landing_pages():
    paths='''<p>Quattro ingressi allo stesso patrimonio: scegli la domanda che ti porta qui.</p><div class="reader-grid">
<section><h2>Capire SpaceX</h2><p>Per cominciare: la storia generale, poi i programmi. Non serve conoscere già motori e orbite.</p><ol><li><a href="storia-spacex.html">I sedici capitoli della storia</a>: dalla fondazione a Block 5.</li><li><a href="../documenti%20per%20sito/falcon9_2017_riutilizzo_accelerazione.html">Perché il riutilizzo cambia il ritmo</a>.</li><li><a href="monografie-spacex.html">Scegli un libro</a> e segui l’indice.</li></ol></section>
<section><h2>Consultare un dato</h2><p>Per chi vuole verificare un numero, una missione o un booster, senza attraversare tutto il racconto.</p><ol><li><a href="storico-lanci.html">Riepilogo e cadenza annuale</a>.</li><li><a href="../archivio/spacex/index.html">Ricerca e filtri dell’archivio operativo</a>.</li><li><a href="../archivio/spacex/metodo.html">Metodo: cosa contano lanci e recuperi</a>.</li></ol></section>
<section><h2>Seguire una missione</h2><p>Le previsioni possono cambiare. Agenda, dossier e registro rispondono a domande diverse.</p><ol><li><a href="lanci-imminenti.html">Agenda dei prossimi lanci</a>.</li><li><a href="starship.html">Stato e dossier Starship</a>.</li><li><a href="../archivio/spacex/elenco.html">Missioni già registrate</a>, con esiti e fonti.</li></ol></section>
<section><h2>Approfondire un programma</h2><p>Per lettori esperti: entra direttamente nell’architettura, poi controlla dipendenze, limiti e fonti.</p><ul><li><a href="../monografie/crew-dragon/index.html">Crew Dragon</a>: sviluppo, sicurezza e servizio.</li><li><a href="../monografie/starlink/index.html">Starlink</a>: rete, OneWeb e megacostellazioni.</li><li><a href="../monografie/starship/index.html">Starship</a>: Raptor, riuso, rifornimento e Marte.</li><li><a href="../monografie/artemis/index.html">Artemis</a>: veicoli, lander e presenza lunare.</li><li><a href="../monografie/starmind/index.html">Starmind</a>: calcolo e infrastrutture orbitali.</li></ul></section></div>
<h2>Tre itinerari trasversali</h2><ul><li><strong>Dal fallimento alla fiducia:</strong> <a href="../documenti%20per%20sito/crs7_crisi_indagine_ripresa_2015.html">CRS-7</a> → <a href="../documenti%20per%20sito/primo_atterraggio_falcon9_2015.html">primo atterraggio</a> → <a href="../monografie/crew-dragon/index.html">certificazione Crew Dragon</a>.</li><li><strong>Dal motore alla missione:</strong> <a href="../monografie/starship/06-raptor-ciclo.html">Raptor</a> → <a href="../monografie/starship/20-rifornimento.html">rifornimento orbitale</a> → <a href="../monografie/artemis/13-starship-hls.html">HLS</a>.</li><li><strong>Dalla rete al cielo condiviso:</strong> <a href="../monografie/starlink/06-architettura.html">architettura Starlink</a> → <a href="../monografie/starlink/16-oneweb.html">OneWeb</a> → <a href="../monografie/starlink/19-cielo-astronomia.html">astronomia</a>.</li></ul><p><a href="cerca-spacex.html">Hai una domanda precisa? Cerca nel testo di tutto il percorso.</a></p>'''
    search='''<p>Ricerca nel testo dei capitoli, delle schede e degli articoli. Per statistiche e filtri sui voli usa anche <a href="../archivio/spacex/index.html">l’archivio operativo</a>.</p><form id="reader-search" class="reader-search" role="search"><label>Parole da cercare<input id="reader-query" name="q" type="search" maxlength="180" placeholder="Es. scudo termico, Red Dragon, SX-0714"></label><label>Tipo di contenuto<select id="reader-type"><option value="">Tutti i tipi</option></select></label><label>Argomento<select id="reader-topic"><option value="">Tutti gli argomenti</option></select></label><button type="submit">Cerca</button></form><p id="reader-status" role="status" aria-live="polite">Caricamento dell’indice…</p><div id="reader-results"></div><button id="reader-more" type="button" hidden>Mostra altri risultati</button><noscript><p>La ricerca full-text richiede JavaScript. Puoi comunque consultare <a href="percorsi-spacex.html">i percorsi</a>, <a href="monografie-spacex.html">gli indici dei libri</a> e <a href="../archivio/spacex/elenco.html">l’elenco statico delle missioni</a>.</p></noscript>'''
    return {'percorsi-spacex':page('Da dove cominciare',paths),'cerca-spacex':page('Cerca in SpaceX',search)}

def update(root=ROOT, check=False):
    # root parametrico permette test su copia isolata, senza workbook reali.
    global ROOT
    ROOT=Path(root)
    pending=[]
    for slug,html in landing_pages().items():
        p=ROOT/'sezioni'/f'{slug}.html';p.parent.mkdir(parents=True,exist_ok=True)
        value=decorate(p,html)
        if not p.exists() or p.read_text(encoding='utf8')!=value:
            pending.append(p)
            if not check:p.write_text(value,encoding='utf8')
    docs=[];changed=[]
    for p in discover():
        # Non includere sorgenti non pubblicati presenti nel worktree.
        if p.name=='spacex_q2_2026_earnings.html':continue
        old=p.read_text(encoding='utf8');new=decorate(p,old)
        if new!=old:
            pending.append(p);changed.append(p)
            if not check:p.write_text(new,encoding='utf8')
        raw=re.sub(r'<!-- LETTORI:NAV -->.*?<!-- /LETTORI:NAV -->','',old,flags=re.S)
        main=re.search(r'<main\b[^>]*>(.*?)</main>',raw,re.S|re.I)
        text=plain(main[1] if main else raw)
        name=title(raw)
        if not text:continue
        docs.append({'url':p.relative_to(ROOT).as_posix(),'title':name,'type':category(p),'topics':[name_ for name_,pattern in TOPICS if re.search(pattern,name+' '+text,re.I)],'text':text})
    index=ROOT/'ricerca/spacex.json';index.parent.mkdir(exist_ok=True)
    value=json.dumps({'version':1,'documents':docs},ensure_ascii=False,separators=(',',':'))+'\n'
    if not index.exists() or index.read_text(encoding='utf8')!=value:
        pending.append(index)
        if not check:index.write_text(value,encoding='utf8')
    if check and pending:
        raise RuntimeError('Navigazione o ricerca da aggiornare: '+', '.join(str(p.relative_to(ROOT)) for p in pending[:10]))
    print(f'Navigazione: {len(changed)} pagine aggiornate; ricerca: {len(docs)} documenti, {len(value.encode("utf8"))} byte.')
    return changed

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--check',action='store_true',help='Verifica senza modificare file')
    args=parser.parse_args();update(args.root,check=args.check)
