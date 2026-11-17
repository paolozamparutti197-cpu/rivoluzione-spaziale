import json
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

SITE = "https://paolozamparutti197-cpu.github.io/rivoluzione-spaziale"
PHOTO_SOURCE = "https://commons.wikimedia.org/wiki/File:Blue_Origin_New_Glenn_Rocket_Successful_Launch_(9387521).jpg"
NASA_ARTEMIS = "https://www.nasa.gov/missions/artemis/nasas-artemis-iii-mission-to-test-future-moon-lander-operations/"
MONTHS = (
    "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
)
PROGRAMS = {
    "shepard": ("New Shepard", "Voli suborbitali"),
    "glenn": ("New Glenn", "Lanci orbitali"),
    "early": ("Prototipi e test", "Prove di volo"),
}


def readable_date(iso_date):
    day = date.fromisoformat(iso_date)
    return f"{day.day} {MONTHS[day.month - 1]} {day.year}"


def time_tag(iso_date):
    return f'<time datetime="{escape(iso_date)}">{readable_date(iso_date)}</time>'


def archive_link(archive_url, program=None, flight=None):
    query = f"?program={quote(program, safe='')}" if program else ""
    fragment = f"#{quote(flight, safe='')}" if flight else ""
    return escape(f"{archive_url}{query}{fragment}")


def render_portal(registry_path, archive_url, photo):
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    flights = data["flights"]
    counts = Counter(flight["program"] for flight in flights)
    latest = max(flights, key=lambda flight: (flight["date"], flight["id"]))
    metrics = "\n".join(
        f"""        <a class="bo-metric" href="{archive_link(archive_url, key)}">
          <span class="bo-metric-value">{counts[key]}</span>
          <span class="bo-metric-name">{name}</span>
          <span class="bo-metric-label">{label}</span>
          <span class="bo-arrow" aria-hidden="true">↗</span>
        </a>"""
        for key, (name, label) in PROGRAMS.items()
    )
    return f"""
<div class="bo-page">
  <a class="bo-skip" href="#bo-cruscotto">Vai ai dati di volo</a>
  <section class="bo-hero" aria-labelledby="bo-title">
    <figure class="bo-hero-media">
      <img src="{escape(photo)}" width="2048" height="1365" fetchpriority="high"
        alt="New Glenn in ascesa sopra le torri di LC-36 e una nube di scarico durante NG-2">
      <figcaption>
        <a href="{archive_link(archive_url, 'glenn', 'NG-2')}">NG-2 · 13 novembre 2025</a>
        <a href="{PHOTO_SOURCE}">Foto Samuel Becker / U.S. Space Force</a>
      </figcaption>
    </figure>
    <div class="bo-wrap bo-hero-copy">
      <h1 id="bo-title">Blue Origin</h1>
      <p>I voli suborbitali dal Texas, il lanciatore orbitale di Cape Canaveral e lo sviluppo dei lander lunari Blue Moon.</p>
      <div class="bo-actions">
        <a class="bo-button" href="{archive_link(archive_url)}">Elenco dei lanci <span aria-hidden="true">↗</span></a>
        <a class="bo-button bo-button-quiet" href="#bo-programmi">Esplora i programmi <span aria-hidden="true">↓</span></a>
      </div>
    </div>
  </section>

  <section class="bo-dashboard" id="bo-cruscotto" aria-labelledby="bo-dashboard-title">
    <div class="bo-wrap">
      <header class="bo-section-head">
        <h2 id="bo-dashboard-title">Dati di volo</h2>
        <p>Registro verificato il {time_tag(data["verifiedOn"])}</p>
      </header>
      <div class="bo-metrics">
{metrics}
      </div>
      <a class="bo-latest" href="{archive_link(archive_url, latest['program'], latest['id'])}">
        <span class="bo-latest-label">Ultimo volo documentato</span>
        <strong>{escape(latest["id"])} · {escape(latest["title"])}</strong>
        {time_tag(latest["date"])}
        <span class="bo-arrow" aria-hidden="true">↗</span>
      </a>
    </div>
  </section>

  <section class="bo-programs" id="bo-programmi" aria-labelledby="bo-programs-title">
    <div class="bo-wrap">
      <header class="bo-section-head">
        <h2 id="bo-programs-title">I programmi</h2>
      </header>
      <div class="bo-program-grid">
        <article class="bo-program bo-program-shepard" id="new-shepard" aria-labelledby="bo-shepard">
          <p class="bo-program-context">Suborbitale · Texas</p>
          <h3 id="bo-shepard">New Shepard</h3>
          <p>Da Launch Site One partono voli con persone, esperimenti scientifici e collaudi. La capsula atterra con paracadute e il booster rientra alla base.</p>
          <div class="bo-program-links">
            <a class="bo-program-link" href="{archive_link(archive_url, 'shepard')}">Voli New Shepard <span aria-hidden="true">↗</span></a>
            <a class="bo-source" href="https://www.blueorigin.com/new-shepard" aria-label="Scheda ufficiale New Shepard">Scheda Blue Origin</a>
          </div>
        </article>
        <article class="bo-program bo-program-glenn" id="new-glenn" aria-labelledby="bo-glenn">
          <p class="bo-program-context">Orbitale · Florida</p>
          <h3 id="bo-glenn">New Glenn</h3>
          <p>Il lanciatore pesante parte dal complesso LC-36. Il primo stadio è progettato per atterrare sulla piattaforma Jacklyn, nell’Atlantico.</p>
          <div class="bo-program-links">
            <a class="bo-program-link" href="{archive_link(archive_url, 'glenn')}">Lanci New Glenn <span aria-hidden="true">↗</span></a>
            <a class="bo-source" href="https://www.blueorigin.com/new-glenn" aria-label="Scheda ufficiale New Glenn">Scheda Blue Origin</a>
          </div>
        </article>
        <article class="bo-program bo-program-moon" id="blue-moon" aria-labelledby="bo-moon">
          <p class="bo-program-context">Lander lunari</p>
          <h3 id="bo-moon">Blue Moon</h3>
          <p>Mark 1 è il lander per carichi e strumenti scientifici. Mark 2 è progettato per portare astronauti tra l’orbita lunare e la superficie nel programma Artemis.</p>
          <div class="bo-program-links">
            <a class="bo-program-link" href="{NASA_ARTEMIS}">Blue Moon nel programma Artemis <span aria-hidden="true">↗</span></a>
            <a class="bo-source" href="https://www.blueorigin.com/blue-moon" aria-label="Scheda ufficiale Blue Moon">Scheda Blue Origin</a>
          </div>
        </article>
      </div>
    </div>
  </section>
</div>
"""


def render_preview(root):
    body = render_portal(root / "dati.json", "elenco.html", "new-glenn-ng2.webp")
    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="I programmi di Blue Origin e l’archivio dei voli di New Shepard e New Glenn.">
  <title>Blue Origin | Rivoluzione Spaziale</title>
  <link rel="stylesheet" href="portale.css">
</head>
<body class="bo-preview">
<header class="topbar">
  <a class="brand" href="{SITE}/index.html">Rivoluzione <span>Spaziale</span></a>
  <nav class="nav" aria-label="Navigazione principale">
    <a href="{SITE}/index.html">Home</a>
    <a href="{SITE}/sezioni/notizie.html">Notizie</a>
    <a href="{SITE}/sezioni/spacex.html">SpaceX</a>
    <a class="active" href="index.html" aria-current="page">Blue Origin</a>
    <a href="{SITE}/sezioni/ula.html">ULA</a>
    <a href="{SITE}/sezioni/electron-lab.html">Electron Lab</a>
    <a href="{SITE}/sezioni/arianespace.html">Arianespace</a>
    <a href="{SITE}/sezioni/cina.html">Cina</a>
  </nav>
</header>
<main>
{body}
</main>
<footer class="footer">Rivoluzione Spaziale</footer>
</body>
</html>
"""


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    (root / "index.html").write_text(render_preview(root), encoding="utf-8", newline="\n")
