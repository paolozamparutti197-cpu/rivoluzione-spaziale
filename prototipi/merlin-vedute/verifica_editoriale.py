"""Conteggio ripetibile del testo della pagina e controllo dei nuovi contenuti."""
from pathlib import Path
from html.parser import HTMLParser
import re, json, unicodedata, subprocess, sys

ROOT=Path(__file__).resolve().parents[2]
class Text(HTMLParser):
    voids={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[];self.parts=[];self.article=[];self.without_sources=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);classes=set(a.get('class','').split())
        p=self.stack[-1] if self.stack else ('',False,False,False,False)
        inside=p[1] or tag=='main'
        skip=p[2] or tag in {'script','style','nav','button'} or 'hidden' in a or bool(classes&{'button','raptor-flow-controls','source-ref'})
        article=p[3] or 'merlin-chapters' in classes
        sources=p[4] or 'sources' in classes
        if tag not in self.voids:self.stack.append((tag,inside,skip,article,sources))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in self.voids:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                del self.stack[i:];break
    def handle_data(self,text):
        if self.stack and self.stack[-1][1] and not self.stack[-1][2]:
            self.parts.append(text)
            if self.stack[-1][3]:self.article.append(text)
            if not self.stack[-1][4]:self.without_sources.append(text)
def clean(parts):return unicodedata.normalize('NFC',' '.join(' '.join(parts).split()))
def count(text):return len(re.findall(r"[^\W_]+(?:[’'\-][^\W_]+)*",text,re.UNICODE))
def parse(html):
    p=Text();p.feed(html);p.close();return p
current=parse((ROOT/'atlante/spacex/merlin.html').read_text(encoding='utf-8'))
old_html=subprocess.check_output(['git','show','229b140:atlante/spacex/merlin.html'],cwd=ROOT).decode('utf-8')
old=parse(old_html)
plain=clean(current.parts)
full=count(plain);without=count(clean(current.without_sources));chapters=count(clean(current.article))
banned=['in sintesi','in conclusione','vale la pena sottolineare','questo evidenzia','non si tratta','è qui che','—']
found=[p for p in banned if p in plain.lower()]
report={'baseline_commit':'229b140','parole_precedenti':count(clean(old.parts)),'parole_finali':full,'parole_senza_bibliografia':without,'parole_capitoli':chapters,'capitoli':len(json.loads((ROOT/'atlante/spacex/merlin-articolo.json').read_text(encoding='utf-8'))['sections']),'formule_da_evitate_trovate':found,'criterio':'Titoli, testo, dati, didascalie e fonti; esclusi menu, comandi e numeri dei rimandi bibliografici. Apostrofi e trattini interni mantengono una sola parola.'}
inventory=ROOT/'00_documentazione/revisioni/merlin_incremento_informativo_20261025.json'
if inventory.exists():
    audit=json.loads(inventory.read_text(encoding='utf-8'))
    assert len(set(x['id'] for x in audit['baseline']))==len(audit['baseline'])
    assert len(set(x['id'] for x in audit['added']))==len(audit['added'])
    data=json.loads((ROOT/'atlante/spacex/schede.json').read_text(encoding='utf-8'))
    article=json.loads((ROOT/'atlante/spacex/merlin-articolo.json').read_text(encoding='utf-8'))
    sections={s['id']:s for s in article['sections']}
    for item in audit['added']:
        assert item['source'] in data['sources'],item['id']
        section=sections[item['section']]
        assert item['evidence'] in ' '.join(section['paragraphs']),item['id']
        assert item['source'] in section['sources'],item['id']
    report['nuclei_precedenti']=len(audit['baseline'])
    report['nuovi_nuclei']=len(audit['added'])
    report['incremento_inventario_percento']=round(100*len(audit['added'])/len(audit['baseline']),1)
    assert len(audit['added'])>=len(audit['baseline'])*.2
print(json.dumps(report,ensure_ascii=False,indent=2))
if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert report['parole_precedenti']==1356
assert full>=3000 and without>=3000,(full,without)
assert not found,found
