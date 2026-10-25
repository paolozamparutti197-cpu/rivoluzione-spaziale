"""Derivati WebP dei render PNG, senza ritagli o modifiche al contenuto."""
from pathlib import Path
from PIL import Image
import json
import sys

root=Path(__file__).resolve().parents[2]
src=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('vedute_png')
dst=root/'assets'/'merlin-vedute'
dst.mkdir(parents=True,exist_ok=True)
names=['insieme','frontale','laterale','gruppo-superiore']
report=[]
for name in names:
    stem='merlin-'+name
    with Image.open(src/(stem+'.png')) as source:
        source.load()
        expected=(1600,1200) if name=='gruppo-superiore' else (1280,1600)
        assert source.size==expected,(name,source.size)
        im=source.convert('RGB')
    im.save(dst/(stem+'.webp'),'WEBP',quality=91,method=6)
    small=im.copy()
    small.thumbnail((640,10000),Image.Resampling.LANCZOS)
    small.save(dst/(stem+'-640.webp'),'WEBP',quality=88,method=6)
    report.append({'id':name,'width':im.width,'height':im.height,'bytes':(dst/(stem+'.webp')).stat().st_size,'small_bytes':(dst/(stem+'-640.webp')).stat().st_size})
print(json.dumps(report,ensure_ascii=False,indent=2))
