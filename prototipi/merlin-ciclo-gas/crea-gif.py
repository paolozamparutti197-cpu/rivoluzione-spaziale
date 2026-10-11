"""Esportazione GIF da fotogrammi originali. Non legge né modifica immagini di terzi."""
from pathlib import Path
from PIL import Image
import json
import numpy as np

ROOT = Path(__file__).resolve().parent
files = sorted((ROOT / 'fotogrammi').glob('*.png'))
if len(files) != 150:
    raise SystemExit(f'Attesi 150 fotogrammi; trovati {len(files)}')

# Una sola palette per tutti i fotogrammi: niente cambi di colore fra un frame e l'altro.
sample = Image.new('RGB', (600 * 4, 434))
for j, index in enumerate((0, 36, 72, 108)):
    with Image.open(files[index]) as img:
        sample.paste(img.convert('RGB').resize((600, 434), Image.Resampling.LANCZOS), (j * 600, 0))
config = json.loads((ROOT / 'flussi.json').read_text(encoding='utf-8'))
primary_hex = list(dict.fromkeys(f['color'] for f in config['flows']))
fixed_hex = primary_hex + ['#f1f6fb', '#adbdcf', '#bfccd8', '#fff4d9', '#0a111d',
                           '#101c2c', '#31465b', '#d8e5ee', '#9db1c3', '#829bb0']
fixed_colors = [tuple(bytes.fromhex(c.lstrip('#'))) for c in fixed_hex]
# Sfumature riservate anche ai bordi antialias delle frecce mobili.
# La riduzione a 256 colori non deve trasformare una variazione morbida in un salto.
for c in primary_hex:
    rgb = tuple(bytes.fromhex(c.lstrip('#')))
    bases = [(10, 17, 29), tuple(round(v*.27+b*.73) for v,b in zip(rgb,(49,70,91)))]
    for base in bases:
        for alpha in (.2, .4, .6, .8):
            fixed_colors.append(tuple(round(v*alpha+b*(1-alpha)) for v,b in zip(rgb,base)))
fixed_colors = list(dict.fromkeys(fixed_colors))
learned_count = 255 - len(fixed_colors)
learned = sample.quantize(colors=learned_count, method=Image.Quantize.MEDIANCUT)
learned_data = learned.getpalette()[:learned_count * 3]
palette_data = [v for rgb in fixed_colors for v in rgb] + learned_data + [0, 0, 0]
palette = Image.new('P', (1, 1))
palette.putpalette(palette_data)
# Indice 255 riservato ai pixel invariati, trasparenti nei frame successivi.
palette_data[765:768] = [0, 0, 0]
palette.putpalette(palette_data)
frames = []
previous = None
for i, file in enumerate(files):
    with Image.open(file) as img:
        full = img.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE)
    pixels = np.asarray(full).copy()
    if np.any(pixels == 255):
        raise SystemExit('Indice della trasparenza usato come colore: palette da rivedere.')
    if previous is None:
        frame = full
    else:
        delta = np.where(pixels != previous, pixels, 255).astype(np.uint8)
        frame = Image.fromarray(delta)
        frame.putpalette(palette_data)
    frame.info['transparency'] = 255
    frames.append(frame)
    previous = pixels
    if i % 24 == 0:
        print(f'Codifica GIF: {i}/{len(files)}', flush=True)

# Esattamente 25 fps: tutti i fotogrammi durano 40 ms, senza cadenza irregolare.
durations = [40] * 150
target = ROOT / 'merlin-ciclo-gas.gif'
frames[0].save(target, save_all=True, append_images=frames[1:], duration=durations,
               loop=0, optimize=False, disposal=1, transparency=255,
               comment=b'Original functional Merlin gas-generator schematic. Rivoluzione Spaziale, 2026-10-11, CC BY 4.0. Not a construction drawing.')
with Image.open(target) as gif:
    duration = 0
    changed = 0
    first = gif.convert('RGB')
    fixed_boxes = {'titolo':(0,0,1800,164),'legenda':(1400,188,1744,627),
                   'bordo-raffreddamento':(1400,649,1744,735),
                   'limiti':(1400,1017,1744,1204),'footer':(0,1224,1800,1300)}
    fixed_reference = {name:first.crop(box).tobytes() for name,box in fixed_boxes.items()}
    key_points = [(1430, 271), (1430, 348), (1430, 425), (1430, 502)]
    with Image.open(files[0]) as source_first:
        source_rgb = source_first.convert('RGB')
        reference_colors = [source_rgb.getpixel(p) for p in key_points]
    gif_colors = [first.getpixel(p) for p in key_points]
    assert reference_colors == gif_colors and len(set(gif_colors)) == 4, (reference_colors, gif_colors)
    for i in range(gif.n_frames):
        gif.seek(i)
        # Il risparmio di peso non deve alterare neppure un pixel della palette.
        with Image.open(files[i]) as src:
            expected = src.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE).convert('RGB')
        if gif.convert('RGB').tobytes() != expected.tobytes():
            raise SystemExit(f'Frame {i}: la composizione GIF non coincide con il render.')
        for name, box in fixed_boxes.items():
            assert gif.convert('RGB').crop(box).tobytes() == fixed_reference[name], (i,name)
        assert gif.info.get('duration') == 40, (i,gif.info.get('duration'))
        duration += gif.info.get('duration', 0)
        if i in (17, 36, 72, 108):
            gif.convert('RGB').save(ROOT / f'controllo-frame-{i:03d}.png')
            if i != 17 and gif.convert('RGB').tobytes() != first.tobytes():
                changed += 1
    report = {'file':str(target),'width':gif.width,'height':gif.height,'frames':gif.n_frames,
              'duration_ms':duration,'loop':gif.info.get('loop'),'bytes':target.stat().st_size,
              'sample_frames_changed':changed,'all_frames_pixel_checked':True,
              'key_colors_preserved_exactly':True,'legend_colors_rgb':gif_colors,
              'uniform_frame_duration_ms':40,'fixed_areas_identical':list(fixed_boxes)}
    assert gif.n_frames == 150 and duration == 6000 and changed == 3, report
    (ROOT / 'verifica-gif.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)
