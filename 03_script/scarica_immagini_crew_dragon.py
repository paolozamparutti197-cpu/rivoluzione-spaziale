"""Acquisisce originali NASA selezionati. Non genera o altera fotografie."""
from pathlib import Path
import json
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

book=Path(__file__).resolve().parents[1]/'monografie'/'crew-dragon'
assets=book/'assets'
assets.mkdir(exist_ok=True)
images=json.loads((book/'immagini.json').read_text(encoding='utf-8'))
for item in images:
    target=assets/item['file']
    if target.exists():
        print('Presente',item['file'])
        continue
    response=requests.get(item['pagina'],timeout=45)
    response.raise_for_status()
    soup=BeautifulSoup(response.text,'html.parser')
    meta=soup.find('meta',property='og:image')
    if not meta:
        raise RuntimeError('Nessuna immagine ufficiale: '+item['pagina'])
    url=meta['content']
    picture=requests.get(url,timeout=60)
    picture.raise_for_status()
    im=Image.open(BytesIO(picture.content))
    im.verify()
    target.write_bytes(picture.content)
    print(item['file'],url,len(picture.content),'bytes')
