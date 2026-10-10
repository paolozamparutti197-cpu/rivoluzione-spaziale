"""Acquisizione meccanica dei soli materiali con licenza registrata."""
from pathlib import Path
import requests,json,shutil
root=Path(__file__).resolve().parents[1];book=root/'monografie/starship';assets=book/'assets';assets.mkdir(exist_ok=True)
local=[
 ('ift5-ignition.jpg','sezioni/assets/sviluppo-starship/starship-ift5-ignition.jpg','Steve Jurvetson','CC BY 2.0','https://commons.wikimedia.org/wiki/File:SpaceX_Starship_ignition_during_IFT-5.jpg'),
 ('ift5-approach.jpg','sezioni/assets/sviluppo-starship/super-heavy-ift5-approach.jpg','Steve Jurvetson','CC BY 2.0','https://commons.wikimedia.org/wiki/File:SpaceX_Starship_booster_landing_approach_IFT-5.jpg'),
 ('its-progetto.jpg','documenti per sito/assets_fondazione/iac-marte-2016/its-progetto.jpg','SpaceX','CC0 storico documentato','https://commons.wikimedia.org/wiki/File:Interplanetary_Transport_System_(29937258496).jpg'),
 ('raptor-2016.jpg','documenti per sito/assets_fondazione/iac-marte-2016/raptor-test-2016.jpg','SpaceX / Elon Musk','CC0 storico documentato','https://commons.wikimedia.org/wiki/File:Raptor-test-9-25-2016.jpg'),
 ('its-marte.jpg','documenti per sito/assets_fondazione/iac-marte-2016/its-su-marte.jpg','SpaceX','CC0 storico documentato','https://commons.wikimedia.org/wiki/File:Interplanetary_Transport_System_(29343824934).jpg')]
registry=[]
for name,path,author,license,source in local:
 shutil.copyfile(root/path,assets/name);registry.append(dict(file=name,autore=author,licenza=license,fonte=source,modifiche='Nessuna ulteriore modifica; stessa risoluzione del file locale con licenza verificata.'));print(name)
remote=[
 ('raptor2-stima.svg','https://upload.wikimedia.org/wikipedia/commons/7/7f/Raptor_2_Full_Flow_Staged_Combustion_Cycle_Estimate.svg','Livingjw e HVM; revisione Nyq','CC BY-SA 4.0','https://commons.wikimedia.org/wiki/File:Raptor_2_Full_Flow_Staged_Combustion_Cycle_Estimate.svg'),
 ('hot-staging-nasa.jpg','https://www.nas.nasa.gov/SC24/assets/images/content/24_Liu_J_SC24_HotStaging_Separation-800.jpg','Jason Howison, NASA/Marshall','Materiale NASA per uso informativo; condizioni NASA','https://www.nas.nasa.gov/SC24/research/project24.php'),
 ('starhopper.jpg','https://upload.wikimedia.org/wikipedia/commons/4/46/Starhopper.jpg','Giuseppe De Chiara','CC BY-SA 4.0','https://commons.wikimedia.org/wiki/File:Starhopper.jpg'),
 ('sn15.jpg','https://upload.wikimedia.org/wikipedia/commons/1/11/Starship_SN15_flap_and_nosecone_(51437260707).jpg','Lars Plougmann','CC BY-SA 2.0','https://commons.wikimedia.org/wiki/File:Starship_SN15_flap_and_nosecone_(51437260707).jpg')]
for name,url,author,license,source in remote:
 r=requests.get(url+('?download=1' if 'wikimedia.org' in url else ''),timeout=40,headers={'User-Agent':'Mozilla/5.0','Referer':'https://commons.wikimedia.org/'});r.raise_for_status()
 if name.endswith('.svg'):
  assert '<svg' in r.text and '<script' not in r.text
 else:assert r.content[:2]==b'\xff\xd8'
 (assets/name).write_bytes(r.content);registry.append(dict(file=name,autore=author,licenza=license,fonte=source,url=url,modifiche='File originale, non modificato.'));print(name,len(r.content))
(book/'immagini.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
