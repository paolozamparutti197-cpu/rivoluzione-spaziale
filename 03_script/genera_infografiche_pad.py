from pathlib import Path
import math
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "pad_di_lancio"
ASSETS = OUT / "assets"
W, H = 1055, 1491

FONT_DIR = Path("C:/Windows/Fonts")
FONT_REG = FONT_DIR / "segoeui.ttf"
FONT_BOLD = FONT_DIR / "segoeuib.ttf"
FONT_ITALIC = FONT_DIR / "segoeuii.ttf"
FONT_LIGHT = FONT_DIR / "segoeuil.ttf"

CYAN = (82, 216, 255)
CYAN_SOFT = (126, 229, 255)
WHITE = (236, 244, 250)
MUTED = (188, 205, 216)
GRID = (35, 155, 190)
DARK = (2, 13, 25)


def font(path, size):
    return ImageFont.truetype(str(path), size=size)


FONTS = {
    "title": font(FONT_BOLD, 138),
    "title_mid": font(FONT_BOLD, 105),
    "title_small": font(FONT_BOLD, 88),
    "subtitle": font(FONT_ITALIC, 40),
    "section": font(FONT_BOLD, 30),
    "year": font(FONT_BOLD, 27),
    "body": font(FONT_REG, 20),
    "body_small": font(FONT_REG, 18),
    "note": font(FONT_REG, 16),
    "box_title": font(FONT_BOLD, 42),
    "info": font(FONT_REG, 19),
}


def wrap_text(draw, text, font_obj, max_width):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        probe = f"{line} {word}".strip()
        if draw.textlength(probe, font=font_obj) <= max_width or not line:
            line = probe
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_wrapped(draw, xy, text, font_obj, fill, max_width, line_gap=4):
    x, y = xy
    lines = wrap_text(draw, text, font_obj, max_width)
    for line in lines:
        draw.text((x, y), line, font=font_obj, fill=fill)
        y += font_obj.size + line_gap
    return y


def rounded(draw, box, radius=14, outline=CYAN, fill=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def build_background(seed, accent=(10, 42, 60)):
    random.seed(seed)
    img = Image.new("RGB", (W, H), DARK)
    px = img.load()
    for y in range(H):
        for x in range(W):
            g = y / H
            r = int(4 + 10 * g + accent[0] * (x / W) * 0.28)
            gg = int(16 + 18 * g + accent[1] * (x / W) * 0.18)
            b = int(31 + 38 * g + accent[2] * (x / W) * 0.20)
            vignette = 1 - 0.55 * math.hypot((x - W * 0.58) / W, (y - H * 0.48) / H)
            noise = random.randint(-4, 4)
            px[x, y] = (
                max(0, min(255, int(r * vignette) + noise)),
                max(0, min(255, int(gg * vignette) + noise)),
                max(0, min(255, int(b * vignette) + noise)),
            )

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for _ in range(42):
        x = random.randint(530, 1060)
        y = random.randint(10, 1150)
        length = random.randint(300, 740)
        d.line((x, y, x + random.randint(-170, 90), y + length), fill=(80, 170, 205, 28), width=1)

    # Industrial silhouettes: tower, umbilical mast, low piping.
    draw_tower(d, 720, 115, 290, 910, alpha=74)
    draw_tower(d, 895, 55, 145, 820, alpha=52)
    d.rectangle((560, 770, 1060, 1210), fill=(5, 16, 24, 88))
    for y in range(910, 1160, 38):
        d.line((520, y, 1100, y + random.randint(-8, 8)), fill=(90, 165, 190, 35), width=2)
    for x in range(560, 1055, 80):
        d.line((x, 900, x + random.randint(-80, 40), 1240), fill=(90, 165, 190, 25), width=2)

    overlay = overlay.filter(ImageFilter.GaussianBlur(0.2))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def cover_resize(img, target_w, target_h):
    scale = max(target_w / img.width, target_h / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - target_w) // 2)
    top = max(0, int((resized.height - target_h) * 0.46))
    return resized.crop((left, top, left + target_w, top + target_h))


def photo_overlay(item):
    photo_name = item.get("photo")
    if not photo_name:
        return None
    path = ASSETS / photo_name
    if not path.exists():
        return None

    y0 = 382
    target_h = H - y0
    img = Image.open(path).convert("RGB")
    img = cover_resize(img, W, target_h)
    img = ImageEnhance.Color(img).enhance(0.48)
    img = ImageEnhance.Contrast(img).enhance(1.28)
    img = ImageEnhance.Brightness(img).enhance(0.78)

    tint = Image.new("RGB", img.size, (0, 62, 84))
    img = Image.blend(img, tint, 0.23).convert("RGBA")

    alpha = Image.new("L", img.size, 0)
    apx = alpha.load()
    for y in range(img.height):
        v = int(54 + 150 * (y / img.height) ** 0.72)
        for x in range(img.width):
            # Softer on the text-heavy left side, clearer on the open right/bottom.
            left_soft = 0.46 + 0.54 * min(1, x / 620)
            apx[x, y] = int(v * left_soft)
    alpha = alpha.filter(ImageFilter.GaussianBlur(10))
    img.putalpha(alpha)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.alpha_composite(img, (0, y0))
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(shade, "RGBA")
    d.rectangle((0, y0, W, H), fill=(0, 8, 15, 18))
    return Image.alpha_composite(layer, shade)


def draw_tower(d, x, y, w, h, alpha=80):
    col = (130, 205, 230, alpha)
    dark = (8, 20, 28, alpha + 30)
    d.rectangle((x, y + h * 0.24, x + w * 0.45, y + h), outline=col, width=2)
    for i in range(10):
        yy = y + h * 0.24 + i * h * 0.074
        d.line((x, yy, x + w * 0.45, yy + h * 0.04), fill=col, width=1)
        d.line((x + w * 0.45, yy, x, yy + h * 0.04), fill=col, width=1)
    d.line((x + w * 0.55, y, x + w * 0.88, y + h), fill=dark, width=5)
    d.line((x + w * 0.82, y, x + w * 0.55, y + h), fill=dark, width=5)
    d.line((x + w * 0.68, y, x + w * 0.68, y + h), fill=col, width=2)
    for i in range(15):
        yy = y + i * h / 15
        d.line((x + w * 0.55, yy, x + w * 0.88, yy + h / 20), fill=col, width=1)


def draw_pin(d, x, y, s, fill=CYAN_SOFT):
    d.ellipse((x + s * 0.25, y, x + s * 0.75, y + s * 0.5), outline=fill, width=4)
    d.polygon([(x + s * 0.5, y + s), (x + s * 0.24, y + s * 0.42), (x + s * 0.76, y + s * 0.42)], fill=fill)
    d.ellipse((x + s * 0.42, y + s * 0.18, x + s * 0.58, y + s * 0.34), fill=(4, 18, 30))


def draw_doc(d, x, y, s, fill=CYAN_SOFT):
    d.rectangle((x + s * 0.18, y + s * 0.08, x + s * 0.78, y + s * 0.90), outline=fill, width=3)
    d.line((x + s * 0.62, y + s * 0.08, x + s * 0.78, y + s * 0.25), fill=fill, width=3)
    for i in range(3):
        yy = y + s * (0.36 + i * 0.16)
        d.line((x + s * 0.30, yy, x + s * 0.66, yy), fill=fill, width=2)


def draw_rocket(d, x, y, s, fill=WHITE):
    d.polygon([(x + s * 0.5, y), (x + s * 0.72, y + s * 0.33), (x + s * 0.66, y + s * 0.78), (x + s * 0.34, y + s * 0.78), (x + s * 0.28, y + s * 0.33)], outline=fill, fill=None)
    d.line((x + s * 0.5, y, x + s * 0.5, y + s * 0.78), fill=fill, width=2)
    d.polygon([(x + s * 0.34, y + s * 0.62), (x + s * 0.10, y + s * 0.96), (x + s * 0.36, y + s * 0.82)], outline=fill, fill=None)
    d.polygon([(x + s * 0.66, y + s * 0.62), (x + s * 0.90, y + s * 0.96), (x + s * 0.64, y + s * 0.82)], outline=fill, fill=None)


def draw_star(d, x, y, s, fill=WHITE):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = s * (0.5 if i % 2 == 0 else 0.22)
        pts.append((x + s * 0.5 + math.cos(a) * r, y + s * 0.5 + math.sin(a) * r))
    d.polygon(pts, fill=fill)


def draw_wrench(d, x, y, s, fill=WHITE):
    d.arc((x + s * 0.04, y + s * 0.02, x + s * 0.52, y + s * 0.50), 40, 310, fill=fill, width=5)
    d.line((x + s * 0.40, y + s * 0.42, x + s * 0.88, y + s * 0.90), fill=fill, width=6)
    d.ellipse((x + s * 0.76, y + s * 0.78, x + s * 0.98, y + s), outline=fill, width=4)


def draw_person(d, x, y, s, fill=WHITE):
    d.ellipse((x + s * 0.35, y + s * 0.06, x + s * 0.65, y + s * 0.36), outline=fill, width=4)
    d.line((x + s * 0.5, y + s * 0.36, x + s * 0.5, y + s * 0.82), fill=fill, width=4)
    d.line((x + s * 0.25, y + s * 0.55, x + s * 0.75, y + s * 0.55), fill=fill, width=4)
    d.line((x + s * 0.5, y + s * 0.82, x + s * 0.28, y + s), fill=fill, width=4)
    d.line((x + s * 0.5, y + s * 0.82, x + s * 0.72, y + s), fill=fill, width=4)


ICONS = [draw_rocket, draw_star, draw_doc, draw_wrench, draw_person]


def draw_header(draw, item):
    title = item["title"]
    tf = FONTS["title"] if len(title) <= 8 else FONTS["title_mid"] if len(title) <= 14 else FONTS["title_small"]
    x, y = 54, 32
    draw.text((x + 3, y + 3), title, font=tf, fill=(0, 0, 0, 130))
    draw.text((x, y), title, font=tf, fill=WHITE)
    line_y = y + tf.size + 16
    draw.line((34, line_y, 690, line_y), fill=CYAN, width=2)
    draw.ellipse((648, line_y - 5, 660, line_y + 7), fill=(190, 246, 255))
    draw_wrapped(draw, (58, line_y + 18), item["subtitle"], FONTS["subtitle"], WHITE, 880, line_gap=2)


def draw_info_box(draw, item):
    x, y, w, h = 52, 276, 545, 128
    rounded(draw, (x, y, x + w, y + h), radius=12, outline=CYAN_SOFT, fill=(5, 26, 42, 158), width=2)
    draw_pin(draw, x + 18, y + 18, 34)
    draw_doc(draw, x + 18, y + 76, 34)
    draw_wrapped(draw, (x + 60, y + 18), f"Localita: {item['location']}", FONTS["info"], WHITE, 455, line_gap=1)
    draw_wrapped(draw, (x + 60, y + 74), f"Nome completo: {item['full']}", FONTS["info"], WHITE, 455, line_gap=1)


def draw_section_label(draw, x, y, text):
    draw.line((x - 20, y + 14, x + 18, y + 14), fill=GRID, width=2)
    draw.text((x + 34, y), text, font=FONTS["section"], fill=CYAN)
    draw.line((x + 250, y + 14, x + 315, y + 14), fill=GRID, width=2)


def draw_timeline(draw, item):
    draw_section_label(draw, 70, 438, "STORIA DEL SITO")
    base_x = 154
    top = 512
    bottom = 1258
    draw.line((base_x, top, base_x, bottom), fill=CYAN_SOFT, width=3)
    events = item["timeline"]
    if len(events) == 1:
        ys = [(top + bottom) // 2]
    else:
        step = (bottom - top) / (len(events) - 1)
        ys = [int(top + i * step) for i in range(len(events))]
    for idx, (event, yy) in enumerate(zip(events, ys)):
        draw.ellipse((base_x - 10, yy - 10, base_x + 10, yy + 10), fill=(225, 255, 255), outline=CYAN, width=2)
        icon = ICONS[idx % len(ICONS)]
        icon(draw, 70, yy - 25, 52, fill=WHITE)
        draw.text((188, yy - 25), event["date"], font=FONTS["year"], fill=CYAN)
        draw_wrapped(draw, (188, yy + 8), event["text"], FONTS["body_small"], WHITE, 360, line_gap=2)


def draw_current_box(draw, item):
    x, y, w, h = 565, 918, 448, 455
    rounded(draw, (x, y, x + w, y + h), radius=20, outline=CYAN, fill=(2, 22, 36, 188), width=2)
    draw_rocket(draw, x + 30, y + 34, 58, fill=CYAN)
    draw.text((x + 92, y + 34), "FASE ATTUALE", font=FONTS["box_title"], fill=CYAN)
    draw.line((x + 260, y + 65, x + w - 35, y + 65), fill=CYAN, width=2)
    yy = y + 108
    for idx, line in enumerate(item["current"]):
        if idx > 0:
            draw.line((x + 20, yy - 15, x + w - 25, yy - 15), fill=(35, 140, 170, 120), width=1)
        ICONS[(idx + 2) % len(ICONS)](draw, x + 28, yy - 2, 36, fill=CYAN)
        yy = draw_wrapped(draw, (x + 82, yy), line, FONTS["body_small"], WHITE, 315, line_gap=2) + 18


def draw_footer(draw, item):
    draw.line((25, 1428, 545, 1428), fill=(38, 148, 178), width=1)
    draw_rocket(draw, 34, 1441, 45, fill=(200, 220, 232))
    draw_wrapped(draw, (80, 1440), item["source_note"], FONTS["note"], (180, 196, 205), 760, line_gap=1)


def create_infographic(item, output_name, seed):
    img = build_background(seed, item.get("accent", (10, 42, 60)))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((0, 0, W, H), fill=(0, 7, 17, 70))
    draw.rectangle((0, 390, 560, 1420), fill=(0, 12, 24, 112))
    photo = photo_overlay(item)
    if photo:
        img = Image.alpha_composite(img, photo)
        draw = ImageDraw.Draw(img, "RGBA")
        draw.rectangle((0, 390, 560, 1420), fill=(0, 12, 24, 72))
    draw_header(draw, item)
    draw_info_box(draw, item)
    draw_timeline(draw, item)
    draw_current_box(draw, item)
    draw_footer(draw, item)
    img.convert("RGB").save(OUT / output_name, quality=95)


PADS = [
    {
        "title": "SLC-40",
        "photo": "slc40.jpg",
        "subtitle": "Il pad workhorse Falcon 9 sulla Space Coast",
        "location": "Cape Canaveral Space Force Station, Florida",
        "full": "Space Launch Complex 40",
        "timeline": [
            {"date": "18 giugno 1965", "text": "Debutta come pad Titan IIIC: SLC-40 nasce per grandi missioni militari dall'Eastern Range."},
            {"date": "Ottobre 2005", "text": "Fine era Titan IV: il complesso viene disattivato e resta una infrastruttura riutilizzabile."},
            {"date": "Maggio 2007", "text": "La 45th Space Wing approva l'accordo che porta SpaceX a operare e modificare SLC-40."},
            {"date": "4 giugno 2010", "text": "Primo volo Falcon 9: la missione dimostrativa raggiunge l'orbita e inaugura l'era SpaceX del pad."},
            {"date": "1 settembre 2016", "text": "Anomalia AMOS-6 durante test statico: il sito viene gravemente danneggiato e poi ricostruito."},
            {"date": "15 dicembre 2017", "text": "CRS-13 segna il ritorno al volo dal pad ricostruito."},
            {"date": "28 settembre 2024", "text": "Crew-9 e' il primo lancio con equipaggio da SLC-40, grazie alla torre di accesso Dragon."},
            {"date": "2026", "text": "LZ-40 entra nel disegno operativo: lancio e rientro RTLS nello stesso complesso in Florida."},
        ],
        "current": [
            "Pad ad alta cadenza per Falcon 9: Starlink, cargo, commerciali e missioni governative.",
            "La torre crew/cargo riduce la dipendenza da LC-39A per Dragon.",
            "Landing Zone 40 dentro il perimetro abilita ritorni a terra piu' compatti.",
            "Il suo valore strategico e' la ridondanza: mantiene la costa est elastica anche con 39A occupato.",
        ],
        "source_note": "Fonti principali: Space Launch Delta 45, NASA press kit CRS, SpaceX launch pages, NASA Crew-12 blog.",
        "accent": (8, 36, 62),
    },
    {
        "title": "LC-39A",
        "photo": "lc39a.jpg",
        "subtitle": "Da Apollo 11 a Dragon, Falcon Heavy e Starship",
        "location": "Kennedy Space Center, Merritt Island, Florida",
        "full": "Launch Complex 39A",
        "timeline": [
            {"date": "9 novembre 1967", "text": "Apollo 4 inaugura il pad con il primo volo Saturn V."},
            {"date": "16 luglio 1969", "text": "Apollo 11 parte da 39A verso il primo allunaggio umano."},
            {"date": "12 aprile 1981", "text": "STS-1 avvia l'era Shuttle dalla stessa rampa."},
            {"date": "8 luglio 2011", "text": "STS-135 chiude la storia operativa dello Space Shuttle."},
            {"date": "15 aprile 2014", "text": "NASA firma con SpaceX un lease ventennale per riusare il pad come sito commerciale."},
            {"date": "19 febbraio 2017", "text": "CRS-10 e' il primo lancio SpaceX da LC-39A."},
            {"date": "6 febbraio 2018", "text": "Falcon Heavy debutta da 39A, con i due side booster che rientrano a Cape Canaveral."},
            {"date": "30 maggio 2020", "text": "Demo-2 riporta lanci orbitali con astronauti dagli Stati Uniti con Crew Dragon."},
            {"date": "2026", "text": "La Final EIS FAA analizza fino a 44 operazioni Starship/Super Heavy annue e infrastrutture associate."},
        ],
        "current": [
            "Pad primario per missioni complesse: Crew Dragon, Falcon Heavy e payload governativi sensibili.",
            "SpaceX ha integrato infrastruttura Apollo/Shuttle con sistemi Falcon e accesso equipaggio.",
            "La traiettoria Starship a 39A e' ambientalmente analizzata, ma resta legata ai requisiti di licenza FAA.",
            "SLC-40 assorbe parte della cadenza Falcon, lasciando 39A piu' disponibile per missioni speciali.",
        ],
        "source_note": "Fonti principali: NASA LC-39A/lease, Space Launch Delta 45, Federal Register FAA Final EIS LC-39A.",
        "accent": (14, 35, 55),
    },
    {
        "title": "SLC-4E",
        "photo": "slc4e.jpeg",
        "subtitle": "La costa ovest Falcon 9 per orbite polari e SSO",
        "location": "Vandenberg Space Force Base, California",
        "full": "Space Launch Complex 4 East",
        "timeline": [
            {"date": "14 agosto 1964", "text": "Il pad debutta con Atlas-Agena per missioni di ricognizione."},
            {"date": "1971-2005", "text": "Lunga fase Titan: Titan IIID, 34D e Titan IV rendono SLC-4E un sito cardine per payload militari."},
            {"date": "2011", "text": "La Final EA valuta il lease SpaceX e la conversione per Falcon 9 e Falcon Heavy."},
            {"date": "29 settembre 2013", "text": "CASSIOPE e' il primo Falcon 9 da Vandenberg e il debutto operativo della famiglia v1.1."},
            {"date": "7 ottobre 2018", "text": "SAOCOM 1A porta il primo atterraggio terrestre SpaceX sulla costa ovest, a LZ-4."},
            {"date": "2024", "text": "La valutazione di cadenza porta SLC-4 verso 50 lanci Falcon 9 annui analizzati."},
            {"date": "2025", "text": "Con il programma Falcon di Vandenberg, SLC-4 resta operativo mentre SLC-6 viene preparato come secondo pad."},
        ],
        "current": [
            "Pad Falcon 9 per orbite polari, eliosincrone e missioni Starlink della costa ovest.",
            "Lavora in coppia con LZ-4, ricavata dall'ex SLC-4W, per i ritorni a terra.",
            "La crescita della cadenza a Vandenberg richiede ridondanza: SLC-6 nasce come secondo binario Falcon.",
            "E' il punto SpaceX piu' naturale per payload che non conviene lanciare dalla Florida.",
        ],
        "source_note": "Fonti principali: SpaceX CASSIOPE/SAOCOM, DAF/VSFB EA Falcon 9 SLC-4E e cadence increase.",
        "accent": (20, 46, 52),
    },
    {
        "title": "SLC-6",
        "photo": "slc6.jpg",
        "subtitle": "Slick Six: da Shuttle mancato a futuro nodo Falcon",
        "location": "Vandenberg Space Force Base, California",
        "full": "Space Launch Complex 6",
        "timeline": [
            {"date": "1966-1969", "text": "Costruito per Titan IIIM e Manned Orbiting Laboratory; il programma MOL viene cancellato prima dell'uso."},
            {"date": "1979-1986", "text": "Ricostruzione per lo Space Shuttle polare: infrastruttura enorme, mai usata per lanci Shuttle."},
            {"date": "15 agosto 1995", "text": "Primo lancio effettivo dal sito con Athena I."},
            {"date": "27 giugno 2006", "text": "Inizia l'era Delta IV con NROL-22."},
            {"date": "20 gennaio 2011", "text": "Primo Delta IV Heavy da Vandenberg."},
            {"date": "24 settembre 2022", "text": "NROL-91 e' l'ultimo Delta IV Heavy da SLC-6; il pad resta vacante."},
            {"date": "24 aprile 2023", "text": "Space Launch Delta 30 autorizza il lease a SpaceX per lanci Falcon."},
            {"date": "10 ottobre 2025", "text": "La ROD DAF autorizza la riqualificazione per Falcon 9/Falcon Heavy e landing operations."},
            {"date": "16 giugno 2026", "text": "Demolizione programmata delle strutture legacy: MST, FUT e Tail Service Masts lasciano spazio ai sistemi Falcon."},
        ],
        "current": [
            "Futuro secondo pad SpaceX a Vandenberg, complementare a SLC-4E.",
            "La DAF ha autorizzato fino a 100 operazioni Falcon annue combinate tra SLC-4 e SLC-6.",
            "Falcon Heavy da Vandenberg e' previsto fino a 5 volte l'anno nell'analisi autorizzata.",
            "La modernizzazione punta ad aumentare capacita' e resilienza della West Coast, con attivazione attesa verso fine 2027 per Falcon 9 e Falcon Heavy.",
        ],
        "source_note": "Fonti principali: NASA MOL, Space Launch Delta 30, ULA NROL-91, DAF Final EIS/ROD Vandenberg Falcon, comunicato VSFB 16/06/2026.",
        "accent": (28, 38, 60),
    },
    {
        "title": "BOCA CHICA PAD 1",
        "photo": "boca1.jpg",
        "subtitle": "OLP-1, il banco prova che ha trasformato Starship in sistema",
        "location": "Starbase, Boca Chica, Texas",
        "full": "Orbital Launch Pad 1 / OLP-1",
        "timeline": [
            {"date": "2014-2021", "text": "SpaceX trasforma Boca Chica da sito sperimentale a complesso Starbase con produzione, test e lancio."},
            {"date": "13 giugno 2022", "text": "La FAA chiude la PEA con mitigazioni: passaggio chiave per il programma Starship/Super Heavy."},
            {"date": "20 aprile 2023", "text": "Primo volo integrato Starship/Super Heavy da OLP-1; il pad subisce danni e viene aggiornato."},
            {"date": "2023", "text": "Arrivano piastra d'acciaio raffreddata ad acqua e deluge: il pad cambia filosofia termica."},
            {"date": "13 ottobre 2024", "text": "Flight 5 dimostra la cattura del booster Super Heavy con la torre Mechazilla."},
            {"date": "Maggio 2025", "text": "La FAA pubblica la decisione per aumentare la cadenza fino a 25 lanci e 25 landings annui."},
            {"date": "2025-2026", "text": "Con Pad 2, Pad 1 passa da unico collo di bottiglia a parte di un sistema Starbase a due rampe."},
        ],
        "current": [
            "OLP-1 e' il pad che ha generato i dati principali su lancio, deluge, catch e turnaround Starship.",
            "La sua funzione evolve: meno singolo punto di fallimento, piu' infrastruttura da aggiornare accanto a Pad 2.",
            "Le operazioni restano sperimentali e dipendono da licenze FAA, finestre aeree/marittime e readiness veicolo.",
            "Il valore storico e' enorme: qui Starship e Super Heavy sono passati dal full stack al recupero del booster.",
        ],
        "source_note": "Fonti principali: FAA Boca Chica project page, Federal Register 2025 cadence, SpaceX Starship Flight 5.",
        "accent": (22, 42, 48),
    },
    {
        "title": "BOCA CHICA PAD 2",
        "photo": "boca2.jpg",
        "subtitle": "OLP-2, la seconda rampa Starship per cadenza e nuova generazione",
        "location": "Starbase, Boca Chica, Texas",
        "full": "Orbital Launch Pad 2 / OLP-2",
        "timeline": [
            {"date": "2024", "text": "SpaceX avvia la seconda torre orbitale a Starbase per ridurre il collo di bottiglia del singolo pad."},
            {"date": "Gennaio 2025", "text": "Le braccia della torre vengono installate: Pad 2 nasce gia' intorno al concetto di stack e catch."},
            {"date": "Maggio 2025", "text": "Il nuovo launch mount viene portato e sollevato nell'area pad, passo visibile verso l'integrazione."},
            {"date": "2025", "text": "Il disegno incorpora lezioni da Pad 1: gestione termica, acqua, flame control e accessi di manutenzione."},
            {"date": "2026", "text": "SpaceX indica Flight 12 come primo volo Starship/Super Heavy V3 e primo lancio da Pad 2."},
            {"date": "2026+", "text": "Pad 2 diventa la rampa di espansione per test V3, maggiore cadenza e ridondanza Starbase."},
        ],
        "current": [
            "Pad 2 e' il salto infrastrutturale: nasce per veicoli Starship piu' maturi e per assorbire lezioni operative.",
            "La ridondanza permette lavori pesanti su un pad mentre l'altro sostiene campagne di test.",
            "Il ruolo atteso e' V3/Block 3: piu' spinta, piu' propellente, maggior pressione su mount e deluge.",
            "La cadenza reale non coincide automaticamente con il massimo ambientale autorizzato: serve readiness completa.",
        ],
        "source_note": "Fonti principali: FAA Boca Chica project page, Federal Register 2025, SpaceX Starship Flight 12, osservazioni NSF.",
        "accent": (10, 48, 58),
    },
]


def main():
    OUT.mkdir(exist_ok=True)
    for i, item in enumerate(PADS, start=1):
        name = item["title"].lower().replace(" ", "_").replace("/", "_")
        create_infographic(item, f"pad_{name}.png", seed=7300 + i)


if __name__ == "__main__":
    main()
