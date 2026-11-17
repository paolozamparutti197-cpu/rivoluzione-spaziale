import json
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROGRAMS = {"shepard": "New Shepard", "glenn": "New Glenn", "early": "Prototipi e test"}
TYPES = {
    "crew": "Suborbitale con equipaggio",
    "science": "Suborbitale di ricerca",
    "test": "Suborbitale di prova",
    "orbital": "Orbitale",
    "atmosphere": "Prova atmosferica",
    "escape": "Fuga dalla rampa",
}
OUTCOMES = {"success": "Riuscito", "failure": "Fallito"}
RECOVERY = {"land": "A terra", "sea": "Su Jacklyn", "lost": "Perso", None: "—"}
MONTHS = (
    "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
)
SITE_URL = "https://paolozamparutti197-cpu.github.io/rivoluzione-spaziale"


def italian_date(value):
    day = date.fromisoformat(value)
    return f"{day.day} {MONTHS[day.month - 1]} {day.year}"


def options(items, default):
    return f'<option value="">{escape(default)}</option>' + "".join(
        f'<option value="{escape(key)}">{escape(label)}</option>'
        for key, label in items.items()
    )


def source_link(source):
    return f'<a href="{escape(source["url"])}">{escape(source["name"])}</a>'


def flight_row(flight):
    row_id = escape(flight["id"])
    day = escape(flight["date"])
    program = flight["program"]
    flight_type = flight["type"]
    outcome = flight["outcome"]
    recovery = flight["recovery"]
    vehicle = escape(flight["vehicle"])
    flight_number = flight["boosterFlight"]
    flight_number_label = (
        f'<small>Volo booster {flight_number}</small>' if flight_number else ""
    )
    links = "".join(f"<li>{source_link(source)}</li>" for source in flight["sources"])
    return f"""      <tr id="{row_id}" data-id="{row_id}" data-date="{day}" data-program="{program}" data-kind="{flight_type}" data-outcome="{outcome}">
        <td>
          <span class="mobile-label">Data e missione</span>
          <time datetime="{day}" data-field="data">{italian_date(day)}</time>
          <a class="mission-id" href="#{row_id}" data-field="id" aria-label="Link alla missione {row_id}">{row_id}</a>
        </td>
        <td>
          <span class="mobile-label">Programma e sito</span>
          <strong data-field="programma">{PROGRAMS[program]}</strong>
          <small data-field="tipo">{TYPES[flight_type]}</small>
          <small data-field="sito">{escape(flight["site"])}</small>
        </td>
        <td>
          <span class="mobile-label">Missione</span>
          <strong data-field="missione">{escape(flight["title"])}</strong>
          <p class="mission-note" data-field="nota">{escape(flight["note"])}</p>
          <details><summary>Fonti</summary><ul>{links}</ul></details>
        </td>
        <td>
          <span class="mobile-label">Veicolo</span>
          <span class="vehicle" data-field="veicolo">{vehicle}</span>{flight_number_label}
        </td>
        <td>
          <span class="mobile-label">Esito missione</span>
          <span class="outcome {outcome}" data-field="esito">{OUTCOMES[outcome]}</span>
        </td>
        <td>
          <span class="mobile-label">Recupero booster</span>
          <span class="recovery" data-field="recupero">{RECOVERY[recovery]}</span>
        </td>
      </tr>"""


def render(data):
    flights = sorted(data["flights"], key=lambda flight: (flight["date"], flight["id"]), reverse=True)
    counts = Counter(flight["program"] for flight in flights)
    years = sorted({flight["date"][:4] for flight in flights}, reverse=True)
    rows = "\n".join(map(flight_row, flights))
    totals = {"": len(flights), **counts}
    metrics = "\n".join(
        f'        <button type="button" class="metric" disabled data-select-program="{value}"'
        f' aria-pressed="{str(not value).lower()}"><strong>{totals[value]}</strong>'
        f'<span>{escape(label)}</span></button>'
        for value, label in {"": "Eventi documentati", **PROGRAMS}.items()
    )
    sources = data["sources"]
    source_list = "\n".join(
        f"          <li>{source_link(sources[key])}</li>"
        for key in ("official", "nsDates", "ngDates", "charon", "goddard", "pm2", "escape", "hotfire")
    )
    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Cronologia dei lanci Blue Origin, dai prototipi ai voli suborbitali di New Shepard e ai lanci orbitali di New Glenn.">
  <title>Elenco dei lanci Blue Origin | Rivoluzione Spaziale</title>
  <link rel="stylesheet" href="archivio.css">
  <script src="archivio.js" defer></script>
</head>
<body>
  <a class="skip" href="#elenco">Vai all’elenco</a>
  <header class="topbar">
    <div class="wrap topbar-inner">
      <a class="brand" href="{SITE_URL}/index.html">Rivoluzione <span>Spaziale</span></a>
      <nav aria-label="Navigazione dell’archivio">
        <a href="{SITE_URL}/sezioni/blue-origin.html">Blue Origin</a>
        <a href="#elenco" aria-current="page">Elenco lanci</a>
        <a href="#metodo">Fonti e criteri</a>
      </nav>
    </div>
  </header>
  <main>
    <div class="intro">
      <div class="wrap">
        <p class="section-name">Archivio Blue Origin</p>
        <h1>Elenco dei lanci</h1>
        <p class="lede">Dai primi voli sperimentali di Charon, Goddard e PM2 ai voli suborbitali di New Shepard e ai lanci orbitali di New Glenn.</p>
        <p class="as-of">Fonti verificate il <time datetime="{escape(data["verifiedOn"])}">{italian_date(data["verifiedOn"])}</time> · Ultimo decollo documentato il <time datetime="{flights[0]["date"]}">{italian_date(flights[0]["date"])}</time></p>
      </div>
    </div>
    <div class="wrap workspace">
      <div class="metrics" aria-label="Numero di eventi per programma">
{metrics}
      </div>
      <section id="elenco" aria-labelledby="elenco-heading">
        <div class="section-head">
          <div>
            <h2 id="elenco-heading">Cronologia</h2>
            <p class="status" id="results-count" role="status">{len(flights)} eventi</p>
          </div>
          <button class="button" id="export" type="button" hidden>Scarica CSV</button>
        </div>
        <form class="filters" id="filters" aria-label="Filtri della cronologia" hidden>
          <label class="search">Cerca
            <input name="q" type="search" placeholder="Es. NS-16, ESCAPADE, PM2">
          </label>
          <label>Programma
            <select name="program">{options(PROGRAMS, "Tutti")}</select>
          </label>
          <label>Anno
            <select name="year">{options(dict(zip(years, years)), "Tutti")}</select>
          </label>
          <label>Tipo di volo
            <select name="kind">{options(TYPES, "Tutti")}</select>
          </label>
          <label>Esito missione
            <select name="outcome">{options(OUTCOMES, "Tutti")}</select>
          </label>
          <label>Ordine
            <select name="sort">
              <option value="desc">Dal più recente</option>
              <option value="asc">Dal più antico</option>
            </select>
          </label>
          <button type="reset" class="button secondary">Azzera filtri</button>
        </form>
        <div class="table-frame">
          <table aria-label="Voli e lanci documentati di Blue Origin">
            <thead>
              <tr>
                <th scope="col">Data e missione</th>
                <th scope="col">Programma e sito</th>
                <th scope="col">Missione</th>
                <th scope="col">Veicolo</th>
                <th scope="col">Esito missione</th>
                <th scope="col">Recupero booster</th>
              </tr>
            </thead>
            <tbody id="flights">
{rows}
            </tbody>
          </table>
          <p class="empty" id="empty" hidden>Nessun evento corrisponde ai filtri.</p>
        </div>
      </section>
      <section class="method" id="metodo" aria-labelledby="metodo-heading">
        <h2 id="metodo-heading">Fonti e criteri</h2>
        <div class="method-columns">
          <div>
            <h3>Che cosa comprende l’elenco</h3>
            <p>La cronologia comprende i decolli numerati da NS-1 a NS-38 e da NG-1 a NG-3, sei voli sperimentali dal 2005 al 2011 e la prova di fuga dalla rampa del 2012. I voli suborbitali comprendono sia i collaudi sia le missioni scientifiche e con persone, anche quando l’obiettivo non è stato raggiunto.</p>
            <p>Le date dei lanci numerati sono in UTC. Per le prove storiche vale la data riportata dalla fonte. Le sigle CH-01, PM1, PM2 e PAD-2012 sono identificativi dell’archivio.</p>
            <p>Scrub, voli in programma e prove con il veicolo a terra sono fuori dal conteggio. L’anomalia di New Glenn del 28 maggio 2026 è avvenuta durante una prova di accensione a terra.</p>
            <h3>Esito e recupero</h3>
            <p>L’esito descrive l’obiettivo primario del volo, come raggiungere la quota di prova o consegnare un carico nell’orbita prevista. NS-1 ha raggiunto la quota prevista e recuperato la capsula. NG-1 ha raggiunto l’orbita prevista. Entrambi hanno perso il booster. NG-3 ha recuperato il booster, mentre BlueBird 7 è stato immesso in un’orbita troppo bassa.</p>
          </div>
          <div>
            <h3>Riferimenti</h3>
            <ul>
{source_list}
            </ul>
            <p>Le fonti specifiche sono riportate nelle singole righe. Per NS-17 e NS-21, la data segue gli aggiornamenti successivi al volo e il riepilogo storico di Blue Origin.</p>
            <p><a href="dati.json">Dati del registro in JSON</a></p>
          </div>
        </div>
      </section>
    </div>
  </main>
  <footer><div class="wrap">Rivoluzione Spaziale · Archivio Blue Origin</div></footer>
</body>
</html>
"""


if __name__ == "__main__":
    data = json.loads((ROOT / "dati.json").read_text(encoding="utf-8"))
    (ROOT / "elenco.html").write_text(render(data), encoding="utf-8", newline="\n")
