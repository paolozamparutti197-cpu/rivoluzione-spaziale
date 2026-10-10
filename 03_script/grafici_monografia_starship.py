"""Grafici editoriali originali: relazioni qualitative e traguardi dal registro."""
from pathlib import Path
from html import escape
import json
BOOK=Path(__file__).resolve().parents[1]/'monografie/starship'
def svg(title,desc,width,height,body):
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d"><title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="#67c7ff"/></marker></defs><rect width="{width}" height="{height}" fill="#0c1520"/><g font-family="Arial,sans-serif"><text x="35" y="45" font-size="27" fill="#f3f5f7">{escape(title)}</text>{body}<text x="35" y="{height-20}" font-size="15" fill="#aab4be">Rivoluzione Spaziale · schema originale · CC BY 4.0</text></g></svg>'
def boxes(name,title,items,note):
 body='';width=1000;height=150+len(items)*125
 for i,(head,desc) in enumerate(items):
  y=85+i*125
  body+=f'<rect x="35" y="{y}" width="930" height="95" rx="8" fill="#132433" stroke="#496a7f"/><text x="60" y="{y+35}" fill="#f5b941" font-size="24">{i+1}. {escape(head)}</text><text x="60" y="{y+70}" fill="#f3f5f7" font-size="20">{escape(desc)}</text>'
  if i<len(items)-1:body+=f'<path d="M500 {y+98}V{y+119}" stroke="#67c7ff" stroke-width="3" marker-end="url(#a)"/>'
 body+=f'<text x="35" y="{height-55}" font-size="17" fill="#aab4be">{escape(note)}</text>'
 (BOOK/'assets'/name).write_text(svg(title,note,width,height,body),encoding='utf-8')
boxes('ciclo-riuso.svg','DOPO IL RITORNO: IL CICLO DEL RIUSO',[
 ('Volo e recupero','Conservare il veicolo per poterlo esaminare.'),
 ('Ispezione','Struttura, motori, protezione e impianti.'),
 ('Interventi','Riparare, sostituire e verificare dove necessario.'),
 ('Accettazione','Decidere se il veicolo è idoneo al nuovo volo.'),
 ('Nuova missione','Il ciclo si ripete; la durata va misurata.')], 'Nessuna durata, costo o quantità di manutenzione viene presunta.')
boxes('rifornimento.svg','RIFORNIMENTO ORBITALE: LE DIPENDENZE',[
 ('Lanci cisterna','Portare propellenti e apparati nell’orbita prevista.'),
 ('Incontro e connessione','Avvicinarsi, accoppiarsi, preparare le linee.'),
 ('Trasferimento e conservazione','Gestire temperatura, pressione, fluidi e perdite.'),
 ('Partenza della nave di missione','Risorse verificate prima della manovra successiva.')], 'Architettura didattica: non è una dimostrazione già compiuta fra due Starship.')
boxes('hls-sequenza.svg','HLS: DUE VEICOLI, COMPITI DIVERSI',[
 ('Starship HLS viene preparata','Rifornimento e trasferimento del lander verso la Luna.'),
 ('Orion porta l’equipaggio','Gli astronauti passano nel lander in area lunare.'),
 ('HLS scende e risale','Missione sulla superficie e ritorno all’incontro.'),
 ('L’equipaggio torna con Orion','Il ritorno terrestre non è un rientro HLS.')], 'Architettura NASA illustrata nel 2024; nessun calendario certo è implicito.')
boxes('marte-catena.svg','MARTE: LA CATENA PRIMA DEL RITORNO',[
 ('Sito e risorse accessibili','Individuare risorse utilizzabili e condizioni del terreno.'),
 ('Energia e impianti','Installare sistemi e farli lavorare in modo continuativo.'),
 ('Produzione dei propellenti','Processi, trattamento, calore e controllo della qualità.'),
 ('Stoccaggio e verifica','Conservare risorse e misurare quelle disponibili.'),
 ('Rifornimento e partenza','Il ritorno dipende dall’intera catena.')], 'Schema concettuale: questi impianti non vengono descritti come già esistenti.')
flights=json.loads((BOOK/'voli.json').read_text(encoding='utf-8'))
chosen=[1,2,4,5,6,9,10,12,14];body='';height=105+95*len(chosen)
for i,n in enumerate(chosen):
 row=flights[n-1];y=105+i*95
 body+=f'<line x1="62" y1="{y-35}" x2="62" y2="{y+58}" stroke="#496a7f" stroke-width="4"/><circle cx="62" cy="{y}" r="10" fill="#f5b941"/><text x="95" y="{y-8}" font-size="18" fill="#aab4be">{row["data"]} · Flight {n}</text><text x="95" y="{y+25}" font-size="26" fill="#f3f5f7">{escape(row["traguardo"])}</text>'
(BOOK/'assets/traguardi.svg').write_text(svg('STARSHIP: PRIME DIMOSTRAZIONI','Cronologia dei primi traguardi dal registro dei voli; non misura della maturità commerciale.',1000,height,body),encoding='utf-8')
print('5 grafici originali generati')
