"""Scarica foto NASA con crediti registrati; non acquisisce materiale di terzi."""
from pathlib import Path
import requests,json
ROOT=Path(__file__).resolve().parents[1];BOOK=ROOT/'monografie/artemis';assets=BOOK/'assets';assets.mkdir(exist_ok=True)
recap='https://www.nasa.gov/general/artemis-ii-mission-milestones-an-image-and-video-recap/'
items=[
 ('lancio1','artemis1-lancio.jpg','https://www.nasa.gov/wp-content/uploads/2024/11/52507883571-396b3c1c6c-o.jpg?w=1600','NASA/Joel Kowsky','https://www.nasa.gov/image-article/two-years-ago-artemis-i-liftoff/','SLS e Orion lasciano LC-39B nel lancio notturno Artemis I','16 novembre 2022: partenza di Artemis I.'),
 ('lancio2','artemis2-lancio.jpg','https://www.nasa.gov/wp-content/uploads/2026/04/nhq202604010230.jpg?w=1600','NASA/Bill Ingalls',recap,'Il lancio di Artemis II da Kennedy il primo aprile 2026','1 aprile 2026: lancio Artemis II, non allunaggio.'),
 ('terra2','artemis2-terra.jpg','https://www.nasa.gov/wp-content/uploads/2026/04/art002e000180.jpg?w=1024','NASA',recap,'La Terra fotografata dall’equipaggio di Orion durante Artemis II','Artemis II: fotografia della Terra durante il viaggio.'),
 ('earthset','artemis2-earthset.jpg','https://www.nasa.gov/wp-content/uploads/2026/04/art002e009288orig.jpg?w=1024','NASA',recap,'La Terra scompare dietro il bordo lunare durante il sorvolo di Artemis II','6 aprile 2026: Earthset osservato durante il sorvolo, non dalla superficie.'),
 ('luna2','artemis2-luna-terra.jpg','https://www.nasa.gov/wp-content/uploads/2026/04/art002e015228orig.jpg?w=1024','NASA',recap,'Luna in primo piano e Terra sullo sfondo fotografate da Orion','Artemis II: la geometria Terra–Luna vista dall’equipaggio.'),
 ('recupero2','artemis2-recupero.jpg','https://www.nasa.gov/wp-content/uploads/2026/04/jsc2026e022260-3695dc.jpg?w=1024','NASA/James Blair',recap,'Operazioni di recupero dell’equipaggio Artemis II nel Pacifico','10 aprile 2026: recupero dopo il ritorno di Artemis II.'),
 ('rs25','rs25-installazione.jpg','https://www.nasa.gov/wp-content/uploads/2023/09/maf_20230908_cs2_eng2059_eng1move44to47-17medium.jpg?w=985','NASA','https://www.nasa.gov/reference/space-launch-system-rs-25-core-stage-engine/','Tecnici installano un motore RS-25 nello stadio centrale SLS','Settembre 2023: installazione RS-25 a Michoud, fotografia di lavorazione.'),
 ('polo','polo-sud-2026.jpg','https://svs.gsfc.nasa.gov/vis/a000000/a004900/a004930/sp_illum_2026_print.jpg',"NASA’s Scientific Visualization Studio; Ernie Wright (USRA), Noah Petro (NASA/GSFC)",'https://svs.gsfc.nasa.gov/4930/','Visualizzazione dell’illuminazione e delle ombre entro due gradi dal polo sud lunare','Visualizzazione geometrica per il 2026, pubblicata nell’atlante NASA 2023–2030. Non è una foto né una carta del ghiaccio.'),
 ('tuta','axemu-prova.jpg','https://www.nasa.gov/wp-content/uploads/2026/02/jsc2025e087229.jpg?w=1024','NASA','https://www.nasa.gov/humans-in-space/nasa-moon-mission-spacesuit-nears-milestone/','Prova AxEMU in piscina durante una simulazione di lavoro sulla superficie','Prova a terra nella Neutral Buoyancy Laboratory, non attività già svolta sulla Luna.')]
registry=[]
for key,name,url,credit,source,alt,caption in items:
 target=assets/name
 if not target.exists():
  r=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=45);r.raise_for_status();assert r.content[:2]==b'\xff\xd8';target.write_bytes(r.content)
 registry.append(dict(id=key,file=name,url=url,credito=credit,fonte=source,alt=alt,didascalia=caption,modifiche='Nessun ritaglio o ritocco; versione alla risoluzione indicata dall’URL NASA.'));print(name,target.stat().st_size)
(BOOK/'immagini.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
