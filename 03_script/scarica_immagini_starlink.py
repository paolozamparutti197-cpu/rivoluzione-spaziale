"""Acquisisce soltanto le immagini documentate nel registro della monografia."""
from pathlib import Path
from io import BytesIO
import requests,json
from PIL import Image
from bs4 import BeautifulSoup
root=Path(__file__).resolve().parents[1]/'monografie'/'starlink'
assets=root/'assets';assets.mkdir(exist_ok=True)
items=json.loads((root/'immagini.json').read_text(encoding='utf-8'))
for file,page,credit,license in [
 ('terra-notte.jpg','https://svs.gsfc.nasa.gov/30876/','NASA’s Goddard Space Flight Center/Joshua Stevens (SSAI), osservazioni Suomi NPP','Uso informativo NASA, vedere pagina SVS e condizioni NASA'),
 ('terminale-alaska.jpg','https://www.flickr.com/photos/alaskanationalguard/54905679447','U.S. Army National Guard/Spc. Ericka Gillespie','Public Domain Mark')]:
 if not any(x['file']==file for x in items):
  r=requests.get(page,timeout=45);r.raise_for_status();s=BeautifulSoup(r.text,'html.parser')
  if file=='terra-notte.jpg':
   a=next(a for a in s.find_all('a',href=True) if 'BlackMarble_2016_global_7km_print.jpg' in a['href']);url=requests.compat.urljoin(page,a['href'])
  else:url=s.select_one('meta[property="og:image"]')['content']
  items.append({'file':file,'url':url,'fonte':page,'credito':credit,'licenza':license})
for x in items:
 p=assets/x['file']
 if not p.exists():
  r=requests.get(x['url'],timeout=60);r.raise_for_status();Image.open(BytesIO(r.content)).verify();p.write_bytes(r.content)
 print(x['file'],Image.open(p).size)
(root/'immagini.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
