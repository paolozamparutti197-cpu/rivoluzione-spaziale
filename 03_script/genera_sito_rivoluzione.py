import json
import re
import subprocess
from datetime import date, datetime
from html import escape
from pathlib import Path

import openpyxl


ROOT = Path(__file__).resolve().parents[1]


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
    source = ROOT / "spacex_lanci_fino_luglio_2026 (1).html"
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
        # Fallback prudente: la sezione resta vuota invece di inventare lanci.
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
    orbits = [
        {"orbita": row.get("orbita"), "lanci": row.get("lanci principali"), "quota": row.get("quota")}
        for row in pad_rows
        if row.get("orbita")
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
    boosters = [
        {
            "booster": row.get("booster"),
            "voli": row.get("voli massimi registrati"),
            "record": row.get("record presenti"),
        }
        for row in landing_rows
        if row.get("booster")
    ][:8]
    return {
        "metrics": metrics,
        "annual": annual,
        "launchers": launchers,
        "pads": pads,
        "orbits": orbits,
        "landing": landing,
        "boosters": boosters,
    }


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
        "range": clean(dashboard["A6"].value),
        "voliRange": clean(dashboard["C6"].value),
        "catchDettaglio": clean(dashboard["E6"].value),
        "reflightDettaglio": clean(dashboard["G6"].value),
        "statoDettaglio": clean(dashboard["I6"].value),
    }
    flights = [
        {
            "flight": row.get("Flight"),
            "data": row.get("Data"),
            "veicolo": row.get("Veicolo"),
            "block": row.get("Block"),
            "milestone": row.get("Milestone"),
            "esito": row.get("Esito integrato"),
            "lezione": row.get("Lezione"),
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
    timeline = [
        {
            "data": row.get("Data"),
            "fase": row.get("Fase"),
            "evento": row.get("Evento"),
            "categoria": row.get("Categoria"),
            "esito": row.get("Esito"),
            "impatto": row.get("Impatto"),
        }
        for row in rows_from_sheet(path, "Timeline integrata", 4)
        if row.get("Data")
    ][-10:]
    return {"metrics": metrics, "flights": flights, "themes": themes, "timeline": timeline}


def json_for_html(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def render():
    data = {
        "upcoming": extract_upcoming_launches(),
        "falcon": falcon_data(),
        "starship": starship_data(),
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    page = f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rivoluzione Spaziale</title>
<style>
:root {{
  --bg:#050607;
  --ink:#f5f7fa;
  --muted:#aeb6bd;
  --line:rgba(255,255,255,.16);
  --panel:rgba(255,255,255,.07);
  --panel2:rgba(255,255,255,.105);
  --accent:#69c8ff;
  --gold:#f2b84b;
  --red:#e45d48;
  --green:#78d58c;
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth;overflow-x:clip}}
*,*::before,*::after{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,Segoe UI,Roboto,Arial,sans-serif;letter-spacing:0;overflow-x:hidden}}
a{{color:inherit;text-decoration:none}}
button{{font:inherit}}
.topbar{{position:fixed;inset:0 0 auto;z-index:30;display:flex;align-items:center;justify-content:space-between;gap:18px;padding:18px clamp(18px,4vw,56px);background:linear-gradient(180deg,rgba(0,0,0,.88),rgba(0,0,0,.48),transparent)}}
.brand{{font-weight:950;letter-spacing:.18em;text-transform:uppercase;font-size:14px}}
.brand span{{color:var(--accent)}}
.nav{{display:flex;gap:16px;flex-wrap:wrap;justify-content:flex-end;font-size:12px;text-transform:uppercase;letter-spacing:.1em;font-weight:850}}
.nav a{{color:#fff;opacity:.82}}
.nav a:hover{{opacity:1;text-decoration:none}}
.hero{{min-height:94vh;display:grid;align-items:end;padding:116px clamp(18px,4vw,56px) 50px;background:linear-gradient(90deg,rgba(0,0,0,.92),rgba(0,0,0,.52) 44%,rgba(0,0,0,.1)),linear-gradient(180deg,rgba(0,0,0,.05),rgba(5,6,7,.96) 92%),url('https://upload.wikimedia.org/wikipedia/commons/5/5d/Falcon_1_Flight_4_launch.jpg') center/cover no-repeat}}
.hero-inner{{max-width:1080px}}
.eyebrow{{margin:0 0 14px;color:var(--gold);font-size:13px;font-weight:900;text-transform:uppercase;letter-spacing:.15em}}
h1{{margin:0;max-width:920px;font-size:clamp(44px,9vw,112px);line-height:.88;text-transform:uppercase;font-weight:950}}
.subtitle{{max-width:780px;margin:24px 0 0;color:#e6ebef;font-size:clamp(18px,2vw,24px);line-height:1.45;font-weight:560}}
.hero-actions{{display:flex;gap:12px;flex-wrap:wrap;margin-top:30px}}
.primary,.secondary{{border:1px solid var(--line);padding:13px 18px;border-radius:4px;text-transform:uppercase;font-size:12px;letter-spacing:.09em;font-weight:900;background:#fff;color:#000;cursor:pointer}}
.secondary{{background:rgba(0,0,0,.22);color:#fff}}
section{{padding:78px clamp(18px,4vw,56px);border-top:1px solid var(--line)}}
.inner{{max-width:1240px;margin:0 auto}}
.section-head{{display:flex;justify-content:space-between;gap:28px;align-items:end;margin-bottom:28px}}
.section-head p{{max-width:640px;color:var(--muted);line-height:1.58;margin:0}}
h2{{margin:0;font-size:clamp(30px,4vw,56px);line-height:.98;text-transform:uppercase}}
h3{{margin:0 0 10px;font-size:22px;line-height:1.14}}
p{{color:#d9dee3;line-height:1.64}}
.powers{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}
.power{{border:1px solid var(--line);background:linear-gradient(180deg,var(--panel2),var(--panel));border-radius:8px;padding:18px;min-height:168px;position:relative;overflow:hidden;transition:transform .18s ease,border-color .18s ease}}
.power:hover{{transform:translateY(-3px);border-color:rgba(105,200,255,.55)}}
.power.active{{border-color:rgba(105,200,255,.8);background:linear-gradient(180deg,rgba(105,200,255,.18),rgba(255,255,255,.065))}}
.power small{{display:block;color:var(--gold);text-transform:uppercase;letter-spacing:.12em;font-weight:900;margin-bottom:36px}}
.power p{{margin:0;color:#cbd2d8;font-size:14px}}
.inactive{{cursor:not-allowed;opacity:.68}}
.split{{display:grid;grid-template-columns:1.05fr .95fr;gap:20px;align-items:stretch}}
.panel{{border:1px solid var(--line);background:rgba(255,255,255,.065);border-radius:8px;padding:22px}}
.spacecopy{{font-size:clamp(20px,2.2vw,29px);line-height:1.38;color:#fff;font-weight:760;margin-top:0}}
.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}
.metric{{border:1px solid var(--line);background:rgba(255,255,255,.065);border-radius:8px;padding:18px;min-height:112px}}
.metric b{{display:block;font-size:clamp(27px,3.5vw,42px);line-height:1;margin-bottom:8px}}
.metric span{{display:block;color:var(--muted);font-size:13px;line-height:1.35}}
.launch-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}
.launch{{border:1px solid var(--line);background:linear-gradient(180deg,rgba(255,255,255,.1),rgba(255,255,255,.05));border-radius:8px;padding:16px;display:flex;flex-direction:column;gap:12px;min-height:282px}}
.launch-top{{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}}
.badge{{display:inline-flex;border:1px solid rgba(105,200,255,.5);color:#dff4ff;border-radius:999px;padding:5px 8px;font-size:11px;text-transform:uppercase;letter-spacing:.08em;font-weight:900}}
.badge.net{{border-color:rgba(242,184,75,.6);color:#ffe1a3}}
.date{{color:#d6dde3;text-align:right;font-size:13px;font-weight:800}}
.launch h3{{font-size:21px}}
.launch p{{margin:0;font-size:14px;color:#cbd2d8}}
.source-links{{display:flex;flex-wrap:wrap;gap:7px;margin-top:2px}}
.source-links a{{border:1px solid rgba(255,255,255,.16);border-radius:999px;padding:5px 8px;color:#dcebf4;font-size:11px;text-transform:uppercase;letter-spacing:.06em;font-weight:850}}
.source-links a:hover{{border-color:rgba(105,200,255,.65);color:#fff}}
.countdown{{margin-top:auto;display:grid;grid-template-columns:repeat(4,1fr);gap:6px}}
.timebox{{background:rgba(0,0,0,.28);border:1px solid rgba(255,255,255,.1);border-radius:6px;padding:8px 4px;text-align:center}}
.timebox strong{{display:block;font-size:20px}}
.timebox span{{display:block;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.08em}}
.dash-grid{{display:grid;grid-template-columns:1.2fr .8fr;gap:18px}}
.bars{{display:grid;gap:8px}}
.bar-row{{display:grid;grid-template-columns:72px 1fr 56px;gap:10px;align-items:center;font-size:13px;color:#dfe5ea}}
.bar{{height:9px;background:rgba(255,255,255,.1);border-radius:999px;overflow:hidden}}
.bar i{{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--green));border-radius:999px}}
table{{width:100%;border-collapse:collapse;font-size:14px}}
th,td{{border-top:1px solid var(--line);padding:12px 8px;text-align:left;vertical-align:top;line-height:1.38}}
th{{color:#fff;text-transform:uppercase;letter-spacing:.08em;font-size:11px}}
td{{color:#d8dee3}}
.cols{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}
.theme-list{{display:grid;gap:12px}}
.theme{{border-left:3px solid var(--accent);padding:0 0 0 14px}}
.theme p{{margin:4px 0 0;font-size:14px;color:#cfd6dc}}
.footer{{padding:34px clamp(18px,4vw,56px);border-top:1px solid var(--line);color:var(--muted);font-size:13px;line-height:1.5}}
.muted{{color:var(--muted)}}
@media(max-width:980px){{.powers,.launch-grid,.metrics{{grid-template-columns:repeat(2,minmax(0,1fr))}}.split,.dash-grid,.cols{{grid-template-columns:1fr}}.nav{{display:none}}}}
@media(max-width:560px){{.powers,.launch-grid,.metrics{{grid-template-columns:1fr}}section{{padding:56px 18px}}.hero{{padding:96px 18px 42px}}h1{{font-size:44px}}.section-head{{display:block}}.bar-row{{grid-template-columns:58px 1fr 44px}}}}
</style>
</head>
<body>
<header class="topbar">
  <div class="brand">Rivoluzione <span>Spaziale</span></div>
  <nav class="nav" aria-label="Navigazione principale">
    <a href="#signori">Mappa</a>
    <a href="#spacex">SpaceX</a>
    <a href="#imminenti">Lanci imminenti</a>
    <a href="#storico">Storico lanci</a>
    <a href="#starship">Starship</a>
  </nav>
</header>
<main>
  <section class="hero">
    <div class="hero-inner">
      <p class="eyebrow">Prima mappa</p>
      <h1>Rivoluzione Spaziale</h1>
      <p class="subtitle">I nuovi signori dello spazio. Non una vetrina celebrativa, ma una dashboard narrativa per seguire chi sta ridisegnando accesso all'orbita, infrastrutture, cadenza e ambizione industriale.</p>
      <div class="hero-actions">
        <a class="primary" href="#spacex">Apri SpaceX</a>
        <a class="secondary" href="#signori">Vedi la mappa</a>
      </div>
    </div>
  </section>

  <section id="signori">
    <div class="inner">
      <div class="section-head">
        <h2>I nuovi signori dello spazio</h2>
        <p>Questa prima versione mette in movimento SpaceX. Le altre aree sono gia impostate come porte del sito, ma restano vuote finche non costruiremo le rispettive sezioni.</p>
      </div>
      <div class="powers" id="powers"></div>
    </div>
  </section>

  <section id="spacex">
    <div class="inner split">
      <article class="panel">
        <p class="eyebrow">Sezione attiva</p>
        <h2>SpaceX</h2>
        <p class="spacecopy">SpaceX e la sezione che per ora tiene acceso il sito: lanci imminenti, storico Falcon e sviluppo Starship. Il tono resta asciutto, operativo, vicino allo stile visuale SpaceX, ma con una lettura da osservatorio.</p>
        <p>La logica e semplice: una pagina d'ingresso che non prova a dire tutto, ma fa capire subito dove si muove oggi la nuova industria spaziale. SpaceX e il primo fronte attivo: calendario, cadenza Falcon, recuperi, riuso e sviluppo Starship nello stesso quadro.</p>
      </article>
      <aside class="panel">
        <h3>Cruscotto SpaceX</h3>
        <p class="muted">Una lettura rapida della macchina operativa: prossimi voli, storico Falcon e maturazione del programma Starship.</p>
        <div class="metrics" id="topMetrics"></div>
      </aside>
    </div>
  </section>

  <section id="imminenti">
    <div class="inner">
      <div class="section-head">
        <h2>Lanci imminenti</h2>
        <p>Tutti i voli gia censiti nella prima agenda, con countdown in tempo reale. I voli NET restano volutamente trattati come finestre indicative.</p>
      </div>
      <div class="launch-grid" id="launchGrid"></div>
    </div>
  </section>

  <section id="storico">
    <div class="inner">
      <div class="section-head">
        <h2>Storico lanci</h2>
        <p>Cruscotto iniziale: riepiloghi, andamento annuale, mix per lanciatore, pad, orbite e recupero booster. I dettagli missione entreranno in una fase successiva.</p>
      </div>
      <div class="metrics" id="falconMetrics"></div>
      <div class="dash-grid" style="margin-top:18px">
        <div class="panel">
          <h3>Lanci per anno</h3>
          <div class="bars" id="annualBars"></div>
        </div>
        <div class="panel">
          <h3>Famiglie Falcon</h3>
          <table id="launcherTable"></table>
        </div>
      </div>
      <div class="cols" style="margin-top:18px">
        <div class="panel"><h3>Pad e aree</h3><table id="padTable"></table></div>
        <div class="panel"><h3>Recupero booster</h3><table id="landingTable"></table></div>
      </div>
    </div>
  </section>

  <section id="starship">
    <div class="inner">
      <div class="section-head">
        <h2>Sviluppo Starship</h2>
        <p>Starship e il laboratorio industriale piu aggressivo della nuova corsa spaziale: non solo un razzo enorme, ma un sistema che prova a unire produzione rapida, riuso completo, rifornimento orbitale e logistica lunare.</p>
      </div>
      <div class="metrics" id="starshipMetrics"></div>
      <div class="dash-grid" style="margin-top:18px">
        <div class="panel"><h3>Voli integrati</h3><table id="starshipFlights"></table></div>
        <div class="panel"><h3>Temi tecnici</h3><div class="theme-list" id="starshipThemes"></div></div>
      </div>
    </div>
  </section>
</main>
<footer class="footer">
  Rivoluzione Spaziale, prima bozza editoriale. Le sezioni non attive sono gia previste nella struttura e verranno sviluppate progressivamente.
</footer>
<script id="site-data" type="application/json">{json_for_html(data)}</script>
<script>
const data = JSON.parse(document.getElementById('site-data').textContent);
const powers = [
  ['SpaceX','Attiva','Lanci, Falcon, Starship','#spacex',true],
  ['Blue Origin','In preparazione','New Glenn, BE-4, lunar economy','#',false],
  ['ULA','In preparazione','Vulcan, national security, transizione post-Atlas','#',false],
  ['Cina','In preparazione','Lunga Marcia, commercial space, stazioni e Luna','#',false],
  ['India','In preparazione','ISRO, LVM3, Gaganyaan, Chandrayaan','#',false],
  ['Giappone','In preparazione','H3, JAXA, ispace e industria privata','#',false],
  ['Europa','In preparazione','Ariane 6, Vega C, sovranita di accesso','#',false],
  ['Italia','In preparazione','Avio, Vega, Space Rider, filiera nazionale','#',false],
];
const fmt = new Intl.NumberFormat('it-IT');
const pct = value => value == null ? 'n.d.' : Math.round(value * 1000) / 10 + '%';
function pad(n){{return String(n).padStart(2,'0')}}
function countdown(iso){{
  const diff = new Date(iso).getTime() - Date.now();
  if (!Number.isFinite(diff) || diff <= 0) return ['0','00','00','00'];
  const total = Math.floor(diff / 1000);
  return [Math.floor(total / 86400), pad(Math.floor(total % 86400 / 3600)), pad(Math.floor(total % 3600 / 60)), pad(total % 60)];
}}
function el(tag, className, html){{
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (html != null) node.innerHTML = html;
  return node;
}}
function renderPowers(){{
  const root = document.getElementById('powers');
  root.innerHTML = powers.map(([name,state,copy,href,active]) => `
    <a class="power ${{active ? 'active' : 'inactive'}}" href="${{href}}" aria-disabled="${{!active}}">
      <small>${{state}}</small><h3>${{name}}</h3><p>${{copy}}</p>
    </a>`).join('');
}}
function metricHTML(value,label){{
  return `<div class="metric"><b>${{value}}</b><span>${{label}}</span></div>`;
}}
function renderMetrics(){{
  const f = data.falcon.metrics;
  document.getElementById('topMetrics').innerHTML = [
    metricHTML(fmt.format(f.lanci),'lanci Falcon principali'),
    metricHTML(pct(f.tasso),'success rate storico'),
    metricHTML(fmt.format(f.recuperiRiusciti),'recuperi booster riusciti'),
    metricHTML(data.starship.metrics.stato || 'n.d.','stato Starship')
  ].join('');
  document.getElementById('falconMetrics').innerHTML = [
    metricHTML(fmt.format(f.lanci),'lanci principali'),
    metricHTML(fmt.format(f.successi),'successi'),
    metricHTML(pct(f.tasso),'tasso successo'),
    metricHTML(fmt.format(f.boosterMax),'max voli booster'),
    metricHTML(fmt.format(f.falconHeavy),'Falcon Heavy'),
    metricHTML(fmt.format(f.padAttivi),'pad attivi'),
    metricHTML(fmt.format(f.tentativiRecupero),'tentativi recupero'),
    metricHTML(fmt.format(f.boosterRiutilizzati),'booster riutilizzati')
  ].join('');
  const s = data.starship.metrics;
  document.getElementById('starshipMetrics').innerHTML = [
    metricHTML(fmt.format(s.eventi),'eventi timeline'),
    metricHTML(fmt.format(s.voli),'voli integrati'),
    metricHTML(fmt.format(s.catch),'catch booster'),
    metricHTML(fmt.format(s.reflight),'reflight Super Heavy')
  ].join('');
}}
function renderLaunches(){{
  const root = document.getElementById('launchGrid');
  root.innerHTML = data.upcoming.map((l) => {{
    const net = (l.cat || []).includes('net');
    const parts = countdown(l.iso);
    const sources = (l.sources || []).map(source => `<a href="${{source.url}}" target="_blank" rel="noopener">${{source.label}}</a>`).join('');
    return `<article class="launch" data-iso="${{l.iso}}">
      <div class="launch-top"><span class="badge ${{net ? 'net' : ''}}">${{net ? 'NET' : 'T-0'}}</span><span class="date">${{l.dateLabel}}</span></div>
      <h3>${{l.name}}</h3>
      <p><strong>${{l.rocket}}</strong></p>
      <p>${{l.site}}</p>
      <p>${{l.payload}}</p>
      <div class="source-links">${{sources}}</div>
      <div class="countdown">
        <div class="timebox"><strong class="d">${{parts[0]}}</strong><span>giorni</span></div>
        <div class="timebox"><strong class="h">${{parts[1]}}</strong><span>ore</span></div>
        <div class="timebox"><strong class="m">${{parts[2]}}</strong><span>min</span></div>
        <div class="timebox"><strong class="s">${{parts[3]}}</strong><span>sec</span></div>
      </div>
    </article>`;
  }}).join('');
}}
function tick(){{
  document.querySelectorAll('.launch[data-iso]').forEach(card => {{
    const parts = countdown(card.dataset.iso);
    card.querySelector('.d').textContent = parts[0];
    card.querySelector('.h').textContent = parts[1];
    card.querySelector('.m').textContent = parts[2];
    card.querySelector('.s').textContent = parts[3];
  }});
}}
function renderAnnual(){{
  const root = document.getElementById('annualBars');
  const rows = data.falcon.annual.filter(x => x.lanci != null);
  const max = Math.max(...rows.map(x => x.lanci));
  root.innerHTML = rows.map(row => `<div class="bar-row"><span>${{row.anno}}</span><div class="bar"><i style="width:${{Math.max(2,row.lanci/max*100)}}%"></i></div><strong>${{row.lanci}}</strong></div>`).join('');
}}
function table(rootId, headers, rows){{
  document.getElementById(rootId).innerHTML = `<thead><tr>${{headers.map(h=>`<th>${{h[0]}}</th>`).join('')}}</tr></thead><tbody>${{rows.map(row => `<tr>${{headers.map(h=>`<td>${{h[1](row) ?? ''}}</td>`).join('')}}</tr>`).join('')}}</tbody>`;
}}
function renderTables(){{
  table('launcherTable', [['Lanciatore',r=>r.lanciatore],['Lanci',r=>fmt.format(r.lanci)],['Successo',r=>pct(r.tasso)]], data.falcon.launchers);
  table('padTable', [['Pad',r=>r.pad],['Lanci',r=>fmt.format(r.lanci)],['Quota',r=>pct(r.quota)]], data.falcon.pads);
  table('landingTable', [['Landing',r=>r.codice],['Record',r=>fmt.format(r.record)],['Recuperi',r=>fmt.format(r.recuperi)]], data.falcon.landing);
  table('starshipFlights', [['Flight',r=>r.flight],['Data',r=>r.data],['Milestone',r=>r.milestone],['Esito',r=>r.esito]], data.starship.flights);
  document.getElementById('starshipThemes').innerHTML = data.starship.themes.map(theme => `<div class="theme"><h3>${{theme.tema}}</h3><p>${{theme.sintesi}}</p><p class="muted">${{theme.impatto}}</p></div>`).join('');
}}
renderPowers();
renderMetrics();
renderLaunches();
renderAnnual();
renderTables();
setInterval(tick, 1000);
</script>
</body>
</html>
"""
    (ROOT / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    render()
