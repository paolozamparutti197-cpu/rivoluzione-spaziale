"""Fotografie documentarie per Starmind; conserva metadata NASA e licenze locali."""
from pathlib import Path
import json, shutil, urllib.request, urllib.parse
ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'monografie/starmind'; A=B/'assets'; A.mkdir(parents=True,exist_ok=True)
REG=[]
NASA=[
('pleiades','ARC-2008-ACD08-0272-005','Supercomputer Pleiades al centro NASA Ames, 2008. Fotografia di un impianto terrestre; non è il computer di AI1.','File di rack del supercomputer Pleiades al centro Ames'),
('spaceborne','iss065e009485','29 aprile 2021: Spaceborne Computer-2 sulla ISS, fotografato da Michael Hopkins. Un precedente di calcolo commerciale in ambiente spaziale, all’interno di una stazione abitata.','Il computer sperimentale Spaceborne Computer-2 installato sulla ISS'),
('radiatori-iss','iss064e041634','13 marzo 2021: Michael Hopkins e Victor Glover lavorano fra pannelli solari e radiatori della ISS. I radiatori sono hardware reale di un sistema diverso da Starmind.','Astronauti in attività extraveicolare accanto ai pannelli e radiatori della ISS'),
('solari-iss','iss065e124482','20 giugno 2021: Shane Kimbrough e Thomas Pesquet completano l’installazione di un pannello solare arrotolabile sulla ISS. Una grande struttura dispiegabile già utilizzata in orbita.','Installazione di un pannello solare arrotolabile sulla struttura della ISS'),
('termovuoto','PIA12021','Dawn viene trasferita in una camera termovuoto. Immagine d’archivio NASA/JPL pubblicata nel 2009; illustra una prova ambientale, non la qualificazione di Starmind.','La sonda Dawn sospesa sopra l’apertura di una camera termovuoto'),
('telescopio-ottico','PIA18577','Telescopio da circa un metro dell’Optical Communications Telescope Laboratory del JPL, immagine pubblicata nel 2014. Stazione sperimentale OPALS, non gateway Starmind.','Il telescopio della stazione ottica OCTL del JPL'),
('opals','iss048e057073','12 agosto 2016: l’apparato OPALS all’esterno della ISS, fotografia di Kate Rubins. Precedente sperimentale di comunicazioni ottiche.','Apparato OPALS montato su una piattaforma esterna della ISS'),
('celle-laboratorio','GRC-2018-C-07373','29 agosto 2018: Tim Peshek mostra una cella sperimentale a perovskite al NASA Glenn. Ricerca sui materiali fotovoltaici; non identifica la tecnologia scelta per AI1.','Ricercatore NASA Glenn mostra una sottile cella fotovoltaica sperimentale'),
('solari-1966','GRC-1966-C-02754','Adolph Spakowski confronta celle convenzionali e celle a film sottile al NASA Lewis nel 1966. L’esigenza di ottenere pannelli leggeri e ripiegabili precede di decenni Starmind.','Adolph Spakowski presenta pannelli e celle solari a film sottile nel 1966'),
('lcrd-lancio','NHQ202112070004','7 dicembre 2021: Atlas V lancia STP-3, con LCRD ospitato a bordo di STPSat-6. Fotografia NASA/Joel Kowsky; non è un lancio SpaceX.','Atlas V lascia la rampa nel lancio del dimostratore di comunicazioni LCRD'),
]
for ident,nid,caption,alt in NASA:
 meta=json.load(urllib.request.urlopen('https://images-api.nasa.gov/search?nasa_id='+urllib.parse.quote(nid),timeout=40))['collection']['items'][0]
 d=meta['data'][0]; assets=json.load(urllib.request.urlopen(meta['href'],timeout=40))
 urls=[x for x in assets if x.endswith('.jpg')]
 url=next((u for u in urls if '~medium.' in u), next((u for u in urls if '~large.' in u),urls[0]))
 dest=A/(ident+'.jpg')
 if not dest.exists():dest.write_bytes(urllib.request.urlopen(url,timeout=60).read())
 credit=d.get('secondary_creator') or d.get('photographer') or 'NASA'
 if not credit.startswith('NASA'):credit='NASA/'+credit
 REG.append(dict(id=ident,file=dest.name,url=url,fonte='https://images.nasa.gov/details/'+nid,credito=credit,licenza='Materiale NASA per uso informativo; attribuzione richiesta',licenza_url='https://www.nasa.gov/nasa-brand-center/images-and-media/',alt=alt,didascalia=caption,modifiche='Nessun ritocco o ritaglio; file alla risoluzione distribuita dalla libreria NASA.',tipo='fotografia documentaria di contesto',metadata_originali=d))
 print(ident,len(dest.read_bytes()))
COPIES=[
('starlink','satelliti-2019.jpg','starlink-satelliti','I satelliti del primo grande gruppo Starlink del maggio 2019, ripresi in orbita prima del rilascio. Documentano una rete di comunicazione, non satelliti AI1.','Il gruppo di satelliti Starlink ancora unito al secondo stadio, con la Terra sullo sfondo'),
('starlink','lancio-2019.jpg','starlink-lancio','Falcon 9 lancia il primo grande gruppo Starlink nel maggio 2019. Un precedente di costruzione seriale della costellazione.','Lancio Falcon 9 del gruppo Starlink del maggio 2019'),
('starlink','treno-satelliti.jpg','tracce-satelliti','Tracce di satelliti in un’immagine astronomica pubblicata da NOIRLab. Il fenomeno è documentato per costellazioni esistenti; non è una misura della luminosità di Starmind.','Tracce di satelliti attraversano un campo stellare osservato da terra'),
('starlink','gemini-south.jpg','gemini-south','L’osservatorio Gemini South in Cile. La qualità del cielo costituisce una risorsa scientifica da includere nelle scelte sulle grandi costellazioni.','Osservatorio Gemini South sotto il cielo notturno'),
('starlink','terminale-alaska.jpg','terminale-alaska','Terminale Starlink durante un’attività della Guardia nazionale in Alaska. Un punto di accesso alla rete terrestre, distinto dal nodo di calcolo orbitale.','Terminale Starlink usato dalla Guardia nazionale in Alaska'),
('starship','ift5-ignition.jpg','starship-decollo','13 ottobre 2024: accensione di Starship durante Flight 5. Fotografia di Steve Jurvetson; illustra il sistema di trasporto, non un lancio Starmind.','Starship e Super Heavy all’accensione del quinto volo integrato'),
('starship','ift5-approach.jpg','superheavy-rientro','13 ottobre 2024: Super Heavy si avvicina alla torre prima della prima cattura. Il recupero del booster è una parte della catena di riuso richiesta dal progetto orbitale.','Super Heavy in avvicinamento alla torre durante Flight 5'),
]
for book,file,ident,caption,alt in COPIES:
 original=next(x for x in json.loads((ROOT/f'monografie/{book}/immagini.json').read_text(encoding='utf8')) if x['file']==file)
 dest=A/(ident+'.jpg');shutil.copy2(ROOT/f'monografie/{book}/assets'/file,dest)
 license=original['licenza'];lu='https://creativecommons.org/publicdomain/zero/1.0/' if 'CC0' in license else 'https://creativecommons.org/publicdomain/mark/1.0/' if 'Public Domain' in license else 'https://creativecommons.org/licenses/by/2.0/' if '2.0' in license else 'https://creativecommons.org/licenses/by/4.0/'
 REG.append(dict(id=ident,file=dest.name,fonte=original['fonte'],url=original.get('url',''),credito=original.get('credito',original.get('autore')),licenza=license,licenza_url=lu,alt=alt,didascalia=caption,modifiche='Copia identica del file del libro '+book+', senza ritocchi o ritagli.',tipo='fotografia documentaria di contesto'))
(B/'immagini.json').write_text(json.dumps(REG,ensure_ascii=False,indent=2),encoding='utf8')
print('Fotografie',len(REG))
