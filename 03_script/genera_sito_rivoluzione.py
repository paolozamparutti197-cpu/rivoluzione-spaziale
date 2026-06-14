import json
import subprocess
from datetime import date, datetime
from html import escape
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parents[1]
SECTIONS_DIR = ROOT / "sezioni"
CSS_DIR = ROOT / "css"

HERO_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/5/5d/Falcon_1_Flight_4_launch.jpg"
CSS_VERSION = "20260614-layout-metriche"

MAIN_SECTIONS = [
    {
        "title": "SpaceX",
        "slug": "spacex",
        "status": "Attiva",
        "copy": "Cadenza Falcon, riuso, agenda lanci e sviluppo Starship.",
        "active": True,
    },
    {
        "title": "Blue Origin",
        "slug": "blue-origin",
        "status": "In costruzione",
        "copy": "New Glenn, BE-4 e il tentativo di costruire un secondo polo privato pesante.",
    },
    {
        "title": "ULA",
        "slug": "ula",
        "status": "In costruzione",
        "copy": "Vulcan, sicurezza nazionale e transizione dalla stagione Atlas/Delta.",
    },
    {
        "title": "Rocket Lab",
        "slug": "rocket-lab",
        "status": "In costruzione",
        "copy": "Electron, Neutron e la via agile al lancio commerciale integrato.",
    },
    {
        "title": "Arianespace",
        "slug": "arianespace",
        "status": "In costruzione",
        "copy": "Ariane 6, Vega C e la ricerca europea di autonomia d'accesso.",
    },
    {
        "title": "Cina",
        "slug": "cina",
        "status": "In costruzione",
        "copy": "Lunga Marcia, stazione spaziale, Luna e nuovo ecosistema commerciale.",
    },
    {
        "title": "Luna",
        "slug": "luna",
        "status": "In costruzione",
        "copy": "Artemis, lander commerciali, basi, risorse e competizione geopolitica.",
    },
    {
        "title": "Marte",
        "slug": "marte",
        "status": "In costruzione",
        "copy": "Dalla retorica della colonizzazione alle tecnologie davvero necessarie.",
    },
    {
        "title": "Infrastrutture orbitali",
        "slug": "infrastrutture-orbitali",
        "status": "In costruzione",
        "copy": "Stazioni private, rifornimento, cargo, servicing e logistica in orbita.",
    },
    {
        "title": "Cronologia",
        "slug": "cronologia",
        "status": "In costruzione",
        "copy": "Una linea del tempo per seguire la rivoluzione spaziale senza perdere il filo.",
    },
]

UTILITY_SECTIONS = [
    {
        "title": "Lanci imminenti",
        "slug": "lanci-imminenti",
        "status": "Attiva",
        "copy": "Agenda SpaceX con countdown e fonti missione.",
    },
    {
        "title": "Storico lanci",
        "slug": "storico-lanci",
        "status": "Attiva",
        "copy": "Dashboard Falcon: cadenza, famiglie, pad e recupero booster.",
    },
    {
        "title": "Starship",
        "slug": "starship",
        "status": "Attiva",
        "copy": "Sviluppo Starship, voli integrati e temi tecnici principali.",
    },
]

ALL_SECTIONS = MAIN_SECTIONS + UTILITY_SECTIONS


def clean(value):
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()[:10]
    if isinstance(value, float):
        return round(value, 4)
    return value


def rows_from_sheet(path, sheet_name, header_row):
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook[sheet_name]
    headers = [cell.value for cell in sheet[header_row]]
    rows = []
    for row in sheet.iter_rows(min_row=header_row + 1, values_only=True):
        if not any(value is not None for value in row):
            continue
        item = {}
        for index, header in enumerate(headers):
            if header is None or index >= len(row):
                continue
            item[str(header)] = clean(row[index])
        rows.append(item)
    return rows


def extract_upcoming_launches():
    node_code = r"""
const fs = require("fs");
const text = fs.readFileSync("spacex_lanci_fino_luglio_2026 (1).html", "utf8");
const match = text.match(/const launches = \[([\s\S]*?)\];/);
if (!match) throw new Error("launches not found");
const launches = Function("return [" + match[1] + "];")();
console.log(JSON.stringify(launches.map((launch) => ({
  id: launch.id,
  cat: launch.cat,
  name: launch.name,
  status: launch.status,
  rocket: launch.rocket,
  dateLabel: launch.dateLabel,
  iso: launch.iso,
  window: launch.window,
  site: launch.site,
  landing: launch.landing,
  orbit: launch.orbit,
  payload: launch.payload,
  summary: launch.summary,
  news: launch.news,
  sources: (launch.sources || []).map((source) => ({ label: source[0], url: source[1] }))
}))));
"""
    try:
        output = subprocess.check_output(["node", "-e", node_code], cwd=ROOT, text=True, encoding="utf-8")
        return json.loads(output)
    except Exception:
        return []


def falcon_data():
    path = ROOT / "01_workbook" / "lanci_spacex_falcon.xlsx"
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    dashboard = workbook["dashboard"]
    metrics = {
        "lanci": clean(dashboard["A4"].value),
        "successi": clean(dashboard["C4"].value),
        "tasso": clean(dashboard["E4"].value),
        "boosterMax": clean(dashboard["G4"].value),
        "falconHeavy": clean(dashboard["I4"].value),
        "padAttivi": clean(dashboard["K4"].value),
        "primo": clean(dashboard["A7"].value),
        "ultimo": clean(dashboard["C7"].value),
        "recordAggiuntivi": clean(dashboard["E7"].value),
        "tentativiRecupero": clean(dashboard["G7"].value),
        "recuperiRiusciti": clean(dashboard["I7"].value),
        "boosterRiutilizzati": clean(dashboard["K7"].value),
    }
    annual = [
        {
            "anno": row.get("anno"),
            "lanci": row.get("lanci principali"),
            "successi": row.get("successi"),
            "falliti": row.get("falliti o parziali"),
            "tasso": row.get("tasso successo"),
        }
        for row in rows_from_sheet(path, "serie_annuale", 3)
        if row.get("anno") is not None
    ]
    launchers = [
        {
            "lanciatore": row.get("lanciatore"),
            "lanci": row.get("lanci principali"),
            "successi": row.get("successi"),
            "tasso": row.get("tasso successo"),
        }
        for row in rows_from_sheet(path, "per_lanciatore", 3)
        if row.get("lanciatore")
    ][:7]
    pad_rows = rows_from_sheet(path, "per_pad_orbita", 3)
    pads = [
        {"pad": row.get("pad"), "lanci": row.get("lanci principali"), "quota": row.get("quota")}
        for row in pad_rows
        if row.get("pad")
    ]
    landing_rows = rows_from_sheet(path, "booster_landing", 3)
    landing = [
        {
            "codice": row.get("codice landing"),
            "record": row.get("record"),
            "tentativi": row.get("tentativi"),
            "recuperi": row.get("recuperi riusciti"),
        }
        for row in landing_rows
        if row.get("codice landing")
    ][:8]
    return {"metrics": metrics, "annual": annual, "launchers": launchers, "pads": pads, "landing": landing}


def starship_data():
    path = ROOT / "01_workbook" / "sviluppo_starship.xlsx"
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    dashboard = workbook["Dashboard"]
    metrics = {
        "eventi": clean(dashboard["A5"].value),
        "voli": clean(dashboard["C5"].value),
        "catch": clean(dashboard["E5"].value),
        "reflight": clean(dashboard["G5"].value),
        "stato": clean(dashboard["I5"].value),
        "statoDettaglio": clean(dashboard["I6"].value),
    }
    flights = [
        {
            "flight": row.get("Flight"),
            "data": row.get("Data"),
            "milestone": row.get("Milestone"),
            "esito": row.get("Esito integrato"),
        }
        for row in rows_from_sheet(path, "Voli integrati", 4)
        if row.get("Flight")
    ]
    themes = [
        {
            "tema": row.get("Tema"),
            "sintesi": row.get("Sintesi integrata"),
            "impatto": row.get("Impatto"),
        }
        for row in rows_from_sheet(path, "Temi e sintesi", 4)
        if row.get("Tema")
    ]
    return {"metrics": metrics, "flights": flights, "themes": themes}


def json_for_html(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def page_path(slug):
    return f"{slug}.html"


def section_href(slug, from_section):
    return page_path(slug) if from_section else f"sezioni/{page_path(slug)}"


def nav_html(current, from_section):
    home_href = "../index.html" if from_section else "index.html"
    links = [("Home", home_href)]
    links.extend((item["title"], section_href(item["slug"], from_section)) for item in ALL_SECTIONS)
    return "\n".join(
        f'<a class="{ "active" if key == current else "" }" href="{href}">{escape(label)}</a>'
        for label, href in links
        for key in [label.lower().replace(" ", "-") if label != "Home" else "home"]
    )


def head_html(title, css_href):
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} | Rivoluzione Spaziale</title>
<link rel="stylesheet" href="{css_href}">
</head>
"""


def shell(title, current, from_section, body, extra_script=""):
    css_path = "../css/style.css" if from_section else "css/style.css"
    css_href = f"{css_path}?v={CSS_VERSION}"
    return f"""{head_html(title, css_href)}
<body>
<header class="topbar">
  <a class="brand" href="{'../index.html' if from_section else 'index.html'}">Rivoluzione <span>Spaziale</span></a>
  <nav class="nav" aria-label="Navigazione principale">
{nav_html(current, from_section)}
  </nav>
</header>
<main>
{body}
</main>
<footer class="footer">
  Rivoluzione Spaziale. Sito statico multipagina pubblicato su GitHub Pages.
</footer>
{extra_script}
</body>
</html>
"""


def metric(value, label):
    return f'<div class="metric"><b>{escape(str(value))}</b><span>{escape(label)}</span></div>'


def percent(value):
    if value is None:
        return "n.d."
    return f"{round(value * 1000) / 10}%"


def render_css():
    return f""":root {{
  --bg:#050607;
  --ink:#f5f7fa;
  --muted:#aeb6bd;
  --line:rgba(255,255,255,.16);
  --panel:rgba(255,255,255,.07);
  --panel2:rgba(255,255,255,.105);
  --accent:#69c8ff;
  --gold:#f2b84b;
  --green:#78d58c;
}}
*,*::before,*::after{{box-sizing:border-box}}
html{{scroll-behavior:smooth;overflow-x:clip}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,Segoe UI,Roboto,Arial,sans-serif;letter-spacing:0;overflow-x:hidden}}
a{{color:inherit;text-decoration:none}}
.topbar{{position:sticky;top:0;z-index:30;display:flex;align-items:center;justify-content:space-between;gap:18px;padding:16px clamp(18px,4vw,56px);background:rgba(5,6,7,.92);border-bottom:1px solid var(--line);backdrop-filter:blur(12px)}}
.brand{{font-weight:950;letter-spacing:.18em;text-transform:uppercase;font-size:14px;white-space:nowrap}}
.brand span{{color:var(--accent)}}
.nav{{display:flex;gap:12px;flex-wrap:wrap;justify-content:flex-end;font-size:11px;text-transform:uppercase;letter-spacing:.08em;font-weight:850}}
.nav a{{color:#fff;opacity:.72}}
.nav a:hover,.nav a.active{{opacity:1;color:#fff}}
.hero{{min-height:76vh;display:grid;align-items:end;padding:110px clamp(18px,4vw,56px) 52px;background:linear-gradient(90deg,rgba(0,0,0,.92),rgba(0,0,0,.54) 45%,rgba(0,0,0,.12)),linear-gradient(180deg,rgba(0,0,0,.08),rgba(5,6,7,.96) 92%),url('{HERO_IMAGE}') center/cover no-repeat}}
.page-hero{{padding:76px clamp(18px,4vw,56px) 44px;border-bottom:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.02))}}
.hero-inner,.inner{{max-width:1240px;margin:0 auto}}
.eyebrow{{margin:0 0 14px;color:var(--gold);font-size:13px;font-weight:900;text-transform:uppercase;letter-spacing:.15em}}
h1{{margin:0;max-width:1000px;font-size:clamp(42px,8vw,106px);line-height:.9;text-transform:uppercase;font-weight:950}}
h2{{margin:0;font-size:clamp(30px,4vw,56px);line-height:.98;text-transform:uppercase}}
h3{{margin:0 0 10px;font-size:22px;line-height:1.14}}
p{{color:#d9dee3;line-height:1.64}}
.subtitle{{max-width:820px;margin:24px 0 0;color:#e6ebef;font-size:clamp(18px,2vw,24px);line-height:1.45;font-weight:560}}
.actions{{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}}
.button{{border:1px solid var(--line);padding:13px 18px;border-radius:4px;text-transform:uppercase;font-size:12px;letter-spacing:.09em;font-weight:900;background:#fff;color:#000}}
.button.secondary{{background:rgba(0,0,0,.22);color:#fff}}
section{{padding:72px clamp(18px,4vw,56px);border-top:1px solid var(--line)}}
.section-head{{display:flex;justify-content:space-between;gap:28px;align-items:end;margin-bottom:28px}}
.section-head p{{max-width:660px;color:var(--muted);line-height:1.58;margin:0}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}}
.card,.panel{{border:1px solid var(--line);background:linear-gradient(180deg,var(--panel2),var(--panel));border-radius:8px;padding:20px}}
.card{{min-height:182px;display:flex;flex-direction:column;justify-content:space-between;transition:transform .18s ease,border-color .18s ease}}
.card:hover{{transform:translateY(-3px);border-color:rgba(105,200,255,.55)}}
.card small,.badge{{color:var(--gold);text-transform:uppercase;letter-spacing:.1em;font-size:11px;font-weight:900}}
.card p{{margin:0;color:#cbd2d8;font-size:14px}}
.split{{display:grid;grid-template-columns:1.05fr .95fr;gap:20px;align-items:stretch}}
.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}
.split .panel .metrics{{grid-template-columns:repeat(2,minmax(0,1fr));margin-top:12px}}
.metric{{min-width:0;border:1px solid var(--line);background:rgba(255,255,255,.065);border-radius:8px;padding:18px;min-height:112px}}
.metric b{{display:block;font-size:clamp(25px,2.6vw,34px);line-height:1.05;margin-bottom:8px;overflow-wrap:break-word}}
.metric span{{display:block;color:var(--muted);font-size:13px;line-height:1.35}}
.launch-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}
.launch{{border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.1),rgba(255,255,255,.05));border-radius:8px;padding:16px;display:flex;flex-direction:column;gap:12px;min-height:318px}}
.launch-top{{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}}
.pill{{display:inline-flex;border:1px solid rgba(105,200,255,.5);color:#dff4ff;border-radius:999px;padding:5px 8px;font-size:11px;text-transform:uppercase;letter-spacing:.08em;font-weight:900}}
.pill.net{{border-color:rgba(242,184,75,.6);color:#ffe1a3}}
.date{{color:#d6dde3;text-align:right;font-size:13px;font-weight:800}}
.launch h3{{font-size:21px}}
.launch p{{margin:0;font-size:14px;color:#cbd2d8}}
.source-links{{display:flex;flex-wrap:wrap;gap:7px;margin-top:2px}}
.source-links a{{border:1px solid rgba(255,255,255,.16);border-radius:999px;padding:5px 8px;color:#dcebf4;font-size:11px;text-transform:uppercase;letter-spacing:.06em;font-weight:850}}
.countdown{{margin-top:auto;display:grid;grid-template-columns:repeat(4,1fr);gap:6px}}
.timebox{{background:rgba(0,0,0,.28);border:1px solid rgba(255,255,255,.1);border-radius:6px;padding:8px 4px;text-align:center}}
.timebox strong{{display:block;font-size:20px}}
.timebox span{{display:block;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.08em}}
.dash-grid{{display:grid;grid-template-columns:1.2fr .8fr;gap:18px}}
.cols{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}
.bars{{display:grid;gap:8px}}
.bar-row{{display:grid;grid-template-columns:72px 1fr 56px;gap:10px;align-items:center;font-size:13px;color:#dfe5ea}}
.bar{{height:9px;background:rgba(255,255,255,.1);border-radius:999px;overflow:hidden}}
.bar i{{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--green));border-radius:999px}}
table{{width:100%;border-collapse:collapse;font-size:14px}}
th,td{{border-top:1px solid var(--line);padding:12px 8px;text-align:left;vertical-align:top;line-height:1.38}}
th{{color:#fff;text-transform:uppercase;letter-spacing:.08em;font-size:11px}}
td{{color:#d8dee3}}
.theme-list{{display:grid;gap:12px}}
.theme{{border-left:3px solid var(--accent);padding:0 0 0 14px}}
.theme p{{margin:4px 0 0;font-size:14px;color:#cfd6dc}}
.construction{{border-color:rgba(242,184,75,.45);background:linear-gradient(180deg,rgba(242,184,75,.12),rgba(255,255,255,.055))}}
.muted{{color:var(--muted)}}
.footer{{padding:34px clamp(18px,4vw,56px);border-top:1px solid var(--line);color:var(--muted);font-size:13px;line-height:1.5}}
@media(max-width:1120px){{.grid,.launch-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}.split,.dash-grid,.cols{{grid-template-columns:1fr}}}}
@media(max-width:760px){{.topbar{{align-items:flex-start;flex-direction:column}}.nav{{justify-content:flex-start}}.grid,.launch-grid,.metrics,.split .panel .metrics{{grid-template-columns:1fr}}section{{padding:56px 18px}}.hero{{padding:92px 18px 42px}}h1{{font-size:43px}}.section-head{{display:block}}.bar-row{{grid-template-columns:58px 1fr 44px}}}}
"""


def render_home():
    cards = "\n".join(
        f"""<a class="card {'construction' if not item.get('active') else ''}" href="sezioni/{item['slug']}.html">
  <small>{escape(item['status'])}</small>
  <div><h3>{escape(item['title'])}</h3><p>{escape(item['copy'])}</p></div>
</a>"""
        for item in MAIN_SECTIONS
    )
    body = f"""
<section class="hero">
  <div class="hero-inner">
    <p class="eyebrow">Osservatorio</p>
    <h1>Rivoluzione Spaziale</h1>
    <p class="subtitle">I nuovi signori dello spazio. Una mappa editoriale per seguire chi sta ridisegnando accesso all'orbita, infrastrutture, Luna, Marte e industria spaziale.</p>
    <div class="actions">
      <a class="button" href="sezioni/spacex.html">Apri SpaceX</a>
      <a class="button secondary" href="sezioni/cronologia.html">Cronologia</a>
    </div>
  </div>
</section>
<section>
  <div class="inner">
    <div class="section-head">
      <h2>Sezioni principali</h2>
      <p>Questa homepage non contiene piu una lunga pagina unica. Ogni blocco importante ha una pagina autonoma, pronta per crescere senza confondere struttura e contenuto.</p>
    </div>
    <div class="grid">{cards}</div>
  </div>
</section>
"""
    return shell("Home", "home", False, body)


def render_launch_cards(launches):
    return "\n".join(
        f"""<article class="launch" data-iso="{escape(str(item.get('iso') or ''))}">
  <div class="launch-top">
    <span class="pill {'net' if 'net' in (item.get('cat') or []) else ''}">{'NET' if 'net' in (item.get('cat') or []) else 'T-0'}</span>
    <span class="date">{escape(str(item.get('dateLabel') or 'Data da confermare'))}</span>
  </div>
  <h3>{escape(str(item.get('name') or 'Missione'))}</h3>
  <p><strong>{escape(str(item.get('rocket') or ''))}</strong></p>
  <p>{escape(str(item.get('site') or ''))}</p>
  <p>{escape(str(item.get('payload') or ''))}</p>
  <div class="source-links">{''.join(f'<a href="{escape(str(src.get("url") or "#"))}" target="_blank" rel="noopener">{escape(str(src.get("label") or "Fonte"))}</a>' for src in item.get("sources", []))}</div>
  <div class="countdown">
    <div class="timebox"><strong class="d">0</strong><span>giorni</span></div>
    <div class="timebox"><strong class="h">00</strong><span>ore</span></div>
    <div class="timebox"><strong class="m">00</strong><span>min</span></div>
    <div class="timebox"><strong class="s">00</strong><span>sec</span></div>
  </div>
</article>"""
        for item in launches
    )


def countdown_script():
    return """<script>
function pad(n){return String(n).padStart(2,'0')}
function countdown(iso){
  const diff = new Date(iso).getTime() - Date.now();
  if (!Number.isFinite(diff) || diff <= 0) return ['0','00','00','00'];
  const total = Math.floor(diff / 1000);
  return [Math.floor(total / 86400), pad(Math.floor(total % 86400 / 3600)), pad(Math.floor(total % 3600 / 60)), pad(total % 60)];
}
function tick(){
  document.querySelectorAll('.launch[data-iso]').forEach(card => {
    const parts = countdown(card.dataset.iso);
    card.querySelector('.d').textContent = parts[0];
    card.querySelector('.h').textContent = parts[1];
    card.querySelector('.m').textContent = parts[2];
    card.querySelector('.s').textContent = parts[3];
  });
}
tick();
setInterval(tick, 1000);
</script>"""


def render_falcon_dashboard(falcon):
    f = falcon["metrics"]
    metric_html = "".join(
        [
            metric(f"{f['lanci']:,}".replace(",", "."), "lanci principali"),
            metric(f"{f['successi']:,}".replace(",", "."), "successi"),
            metric(percent(f["tasso"]), "tasso successo"),
            metric(f["boosterMax"], "max voli booster"),
            metric(f["falconHeavy"], "Falcon Heavy"),
            metric(f["padAttivi"], "pad attivi"),
            metric(f["recuperiRiusciti"], "recuperi booster"),
            metric(f["boosterRiutilizzati"], "booster riutilizzati"),
        ]
    )
    max_launches = max(row["lanci"] or 0 for row in falcon["annual"]) or 1
    bars = "\n".join(
        f"""<div class="bar-row"><span>{row['anno']}</span><div class="bar"><i style="width:{max(2, (row['lanci'] or 0) / max_launches * 100)}%"></i></div><strong>{row['lanci']}</strong></div>"""
        for row in falcon["annual"]
    )
    launcher_rows = "\n".join(
        f"<tr><td>{escape(str(row['lanciatore']))}</td><td>{row['lanci']}</td><td>{percent(row['tasso'])}</td></tr>"
        for row in falcon["launchers"]
    )
    pad_rows = "\n".join(
        f"<tr><td>{escape(str(row['pad']))}</td><td>{row['lanci']}</td><td>{percent(row['quota'])}</td></tr>"
        for row in falcon["pads"]
    )
    landing_rows = "\n".join(
        f"<tr><td>{escape(str(row['codice']))}</td><td>{row['record']}</td><td>{row['recuperi']}</td></tr>"
        for row in falcon["landing"]
    )
    return f"""
<div class="metrics">{metric_html}</div>
<div class="dash-grid" style="margin-top:18px">
  <div class="panel"><h3>Lanci per anno</h3><div class="bars">{bars}</div></div>
  <div class="panel"><h3>Famiglie Falcon</h3><table><thead><tr><th>Lanciatore</th><th>Lanci</th><th>Successo</th></tr></thead><tbody>{launcher_rows}</tbody></table></div>
</div>
<div class="cols" style="margin-top:18px">
  <div class="panel"><h3>Pad e aree</h3><table><thead><tr><th>Pad</th><th>Lanci</th><th>Quota</th></tr></thead><tbody>{pad_rows}</tbody></table></div>
  <div class="panel"><h3>Recupero booster</h3><table><thead><tr><th>Landing</th><th>Record</th><th>Recuperi</th></tr></thead><tbody>{landing_rows}</tbody></table></div>
</div>
"""


def render_starship(starship):
    s = starship["metrics"]
    metric_html = "".join(
        [
            metric(s["eventi"], "eventi timeline"),
            metric(s["voli"], "voli integrati"),
            metric(s["catch"], "catch booster"),
            metric(s["reflight"], "reflight Super Heavy"),
        ]
    )
    flight_rows = "\n".join(
        f"<tr><td>{escape(str(row['flight']))}</td><td>{escape(str(row['data']))}</td><td>{escape(str(row['milestone']))}</td><td>{escape(str(row['esito']))}</td></tr>"
        for row in starship["flights"]
    )
    themes = "\n".join(
        f"""<div class="theme"><h3>{escape(str(row['tema']))}</h3><p>{escape(str(row['sintesi']))}</p><p class="muted">{escape(str(row['impatto']))}</p></div>"""
        for row in starship["themes"]
    )
    return f"""
<div class="metrics">{metric_html}</div>
<div class="dash-grid" style="margin-top:18px">
  <div class="panel"><h3>Voli integrati</h3><table><thead><tr><th>Flight</th><th>Data</th><th>Milestone</th><th>Esito</th></tr></thead><tbody>{flight_rows}</tbody></table></div>
  <div class="panel"><h3>Temi tecnici</h3><div class="theme-list">{themes}</div></div>
</div>
"""


def page_hero(title, eyebrow, copy, construction=False):
    badge = '<p class="badge">Pagina in costruzione</p>' if construction else ""
    return f"""
<section class="page-hero">
  <div class="inner">
    <p class="eyebrow">{escape(eyebrow)}</p>
    <h1>{escape(title)}</h1>
    <p class="subtitle">{escape(copy)}</p>
    {badge}
  </div>
</section>
"""


def render_spacex(data):
    f = data["falcon"]["metrics"]
    top_metrics = "".join(
        [
            metric(f"{f['lanci']:,}".replace(",", "."), "lanci Falcon principali"),
            metric(percent(f["tasso"]), "success rate storico"),
            metric(f["recuperiRiusciti"], "recuperi booster riusciti"),
            metric(data["starship"]["metrics"]["stato"], "stato Starship"),
        ]
    )
    body = f"""
{page_hero("SpaceX", "Sezione attiva", "L'area SpaceX raccoglie la parte viva del sito: agenda dei lanci, storico Falcon, riuso dei booster e sviluppo Starship.")}
<section>
  <div class="inner split">
    <article class="panel">
      <h2>Macchina operativa</h2>
      <p>SpaceX non viene trattata come una semplice azienda di lanci. Qui e il primo laboratorio della nuova industria spaziale: cadenza, costi, recupero, riuso, infrastrutture e sviluppo rapido nello stesso sistema.</p>
      <div class="actions">
        <a class="button" href="lanci-imminenti.html">Lanci imminenti</a>
        <a class="button secondary" href="storico-lanci.html">Storico lanci</a>
        <a class="button secondary" href="starship.html">Starship</a>
      </div>
    </article>
    <aside class="panel"><h3>Cruscotto rapido</h3><div class="metrics">{top_metrics}</div></aside>
  </div>
</section>
"""
    return shell("SpaceX", "spacex", True, body)


def render_launches_page(data):
    body = f"""
{page_hero("Lanci imminenti", "Agenda SpaceX", "Tutti i voli gia censiti nella prima agenda, con countdown in tempo reale. I voli NET restano finestre indicative.")}
<section>
  <div class="inner">
    <div class="launch-grid">{render_launch_cards(data['upcoming'])}</div>
  </div>
</section>
"""
    return shell("Lanci imminenti", "lanci-imminenti", True, body, countdown_script())


def render_history_page(data):
    body = f"""
{page_hero("Storico lanci", "Dashboard Falcon", "Riepilogo operativo dello storico Falcon: cadenza, successi, pad, famiglie di lanciatore e recupero booster.")}
<section>
  <div class="inner">{render_falcon_dashboard(data['falcon'])}</div>
</section>
"""
    return shell("Storico lanci", "storico-lanci", True, body)


def render_starship_page(data):
    body = f"""
{page_hero("Starship", "Sviluppo SpaceX", "Produzione rapida, riuso completo, rifornimento orbitale e logistica lunare: Starship merita una pagina separata dalla porta generale SpaceX.")}
<section>
  <div class="inner">{render_starship(data['starship'])}</div>
</section>
"""
    return shell("Starship", "starship", True, body)


def render_placeholder(item):
    body = f"""
{page_hero(item['title'], item['status'], item['copy'], construction=True)}
<section>
  <div class="inner split">
    <article class="panel construction">
      <h2>In costruzione</h2>
      <p>Questa pagina e gia separata nella struttura del sito, ma il contenuto editoriale verra sviluppato in una fase successiva. Per ora resta come porta autonoma, con navigazione coerente e percorsi gia pronti per GitHub Pages.</p>
    </article>
    <aside class="panel">
      <h3>Prossimo sviluppo</h3>
      <p class="muted">Qui entreranno contesto, cronologia, dati, fonti e collegamenti alle pagine correlate.</p>
    </aside>
  </div>
</section>
"""
    return shell(item["title"], item["slug"], True, body)


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render():
    data = {
        "upcoming": extract_upcoming_launches(),
        "falcon": falcon_data(),
        "starship": starship_data(),
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    write(CSS_DIR / "style.css", render_css())
    write(ROOT / "index.html", render_home())
    write(SECTIONS_DIR / "spacex.html", render_spacex(data))
    write(SECTIONS_DIR / "lanci-imminenti.html", render_launches_page(data))
    write(SECTIONS_DIR / "storico-lanci.html", render_history_page(data))
    write(SECTIONS_DIR / "starship.html", render_starship_page(data))
    for item in MAIN_SECTIONS:
        if item["slug"] != "spacex":
            write(SECTIONS_DIR / f"{item['slug']}.html", render_placeholder(item))


if __name__ == "__main__":
    render()
