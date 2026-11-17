import json
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote, urlencode

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


def archive_link(archive_url, program=None, flight=None, kind=None):
    filters = {key: value for key, value in (("program", program), ("kind", kind)) if value}
    query = f"?{urlencode(filters)}" if filters else ""
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
            <a class="bo-program-link" href="new-shepard.html">Dossier New Shepard <span aria-hidden="true">↗</span></a>
            <a class="bo-source" href="{archive_link(archive_url, 'shepard')}">Voli New Shepard</a>
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


NS_DESCRIPTION = (
    "Come vola New Shepard, dalle prime prove di riuso ai voli con equipaggio "
    "e agli esperimenti in gravità lunare simulata."
)
NS_MILESTONES = (
    (
        "NS-1", "Il primo volo di sviluppo",
        "La capsula si separa e torna a terra dopo un volo alla quota di prova di circa 93,5 km. "
        "Il booster perde pressione nel circuito idraulico in discesa e va perso.",
    ),
    (
        "NS-2", "Il primo atterraggio del booster",
        "New Shepard supera i 100 km. Il BE-3 si riaccende per frenare il booster, "
        "che atterra in verticale sulla piattaforma.",
    ),
    (
        "NS-3", "Lo stesso booster vola di nuovo",
        "Il modulo propulsivo di NS-2 riparte e atterra una seconda volta. "
        "Il programma verifica così il riuso in volo dell’hardware recuperato.",
    ),
    (
        "NS-6", "La prova di fuga in ascesa",
        "Il motore di fuga allontana la capsula dal razzo come previsto dal collaudo. "
        "La capsula scende con i paracadute e il booster atterra separatamente.",
    ),
    (
        "NS-16", "Il primo equipaggio",
        "Jeff Bezos, Mark Bezos, Wally Funk e Oliver Daemen superano la linea di Kármán "
        "e tornano nel Texas occidentale.",
    ),
    (
        "NS-23", "L’emergenza in volo",
        "Durante una missione senza equipaggio cede l’ugello del motore. Il sistema di fuga "
        "separa la capsula, che atterra con i carichi. Il booster si distrugge all’impatto.",
    ),
    (
        "NS-24", "Il ritorno al volo",
        "Il programma riprende dopo l’incidente con una missione senza equipaggio "
        "che porta 33 carichi di ricerca e tecnologia.",
    ),
    (
        "NS-29", "Un volo per la ricerca lunare",
        "La capsula ruota durante il tratto in microgravità per far sperimentare ai carichi "
        "un’accelerazione simile a quella di gravità sulla Luna.",
    ),
    (
        "NS-38", "Il volo prima della pausa",
        "Sei persone volano da Launch Site One. Le immagini del dossier mostrano il decollo "
        "e il ritorno dei due veicoli durante questa missione.",
    ),
)


def render_new_shepard(registry_path, portal_url, archive_url, assets_url):
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    flights = {
        flight["id"]: flight for flight in data["flights"]
        if flight["program"] == "shepard"
    }
    crewed = sum(flight["type"] == "crew" for flight in flights.values())
    recovered = sum(flight["recovery"] == "land" for flight in flights.values())
    all_flights = archive_link(archive_url, "shepard")
    crew_flights = archive_link(archive_url, "shepard", kind="crew")
    research_flights = archive_link(archive_url, "shepard", kind="science")
    lunar_flight = archive_link(archive_url, "shepard", "NS-29")
    launch_photo = escape(assets_url + "/ns38-lancio.webp")
    booster_photo = escape(assets_url + "/ns38-booster.webp")
    capsule_photo = escape(assets_url + "/ns38-capsula.webp")

    milestones = []
    for mission, title, description in NS_MILESTONES:
        row = flights[mission]
        extra_source = (
            '<a class="ns-source" href="https://www.faa.gov/newsroom/faa-closes-blue-origin-mishap-investigation">'
            'Conclusioni dell’indagine FAA</a>'
            if mission == "NS-23" else ""
        )
        milestones.append(f"""        <li class="ns-milestone" id="tappa-{mission.lower()}">
          <div class="ns-date">
            {time_tag(row["date"])}
            <span class="ns-mission">{mission}</span>
          </div>
          <div class="ns-milestone-story">
            <h3>{escape(title)}</h3>
            <p>{escape(description)}</p>
            {extra_source}
          </div>
          <a class="ns-record-link" href="{archive_link(archive_url, 'shepard', mission)}"
            aria-label="Apri {mission} nell’archivio">Archivio {mission} <span aria-hidden="true">↗</span></a>
        </li>""")
    timeline = "\n".join(milestones)
    return f"""
<div class="bo-page ns-page">
  <a class="bo-skip" href="#ns-profilo">Vai al profilo di volo</a>
  <div class="bo-wrap ns-breadcrumb">
    <a href="{escape(portal_url)}"><span aria-hidden="true">←</span> Blue Origin</a>
  </div>

  <section class="ns-hero" aria-labelledby="ns-title">
    <div class="bo-wrap ns-hero-grid">
      <div class="ns-hero-copy">
        <p class="ns-context">Voli suborbitali · Texas</p>
        <h1 id="ns-title">New Shepard</h1>
        <p class="ns-lede">Una capsula e un booster riutilizzabili. Partono insieme da Launch Site One, si separano in volo e tornano a terra con due sistemi di atterraggio diversi.</p>
        <div class="bo-actions">
          <a class="bo-button" href="#ns-profilo">Segui il profilo di volo <span aria-hidden="true">↓</span></a>
          <a class="bo-button bo-button-quiet" href="{all_flights}">Archivio New Shepard <span aria-hidden="true">↗</span></a>
        </div>
      </div>
      <figure class="ns-hero-photo">
        <img src="{launch_photo}" fetchpriority="high"
          alt="New Shepard si solleva dalla rampa nel Texas occidentale durante NS-38">
        <figcaption>Decollo di NS-38, 22 gennaio 2026.
          <a href="https://www.blueorigin.com/gallery/asset/6972c92fc8b28f2654a8abf3">Foto Blue Origin</a>
        </figcaption>
      </figure>
    </div>
  </section>

  <div class="ns-register">
    <div class="bo-wrap">
      <dl class="ns-register-grid">
        <div><dt>Voli documentati</dt><dd>{len(flights)}</dd></div>
        <div><dt>Voli con equipaggio</dt><dd>{crewed}</dd></div>
        <div><dt>Atterraggi del booster riusciti</dt><dd>{recovered}</dd></div>
      </dl>
      <p>Registro verificato il {time_tag(data["verifiedOn"])}.</p>
    </div>
  </div>

  <nav class="bo-wrap ns-jump" aria-label="Indice del dossier">
    <a href="#ns-profilo">Profilo di volo</a>
    <a href="#ns-cronologia">Missioni chiave</a>
    <a href="#ns-ricerca">Persone e ricerca</a>
  </nav>

  <section class="ns-section" id="ns-profilo" aria-labelledby="ns-profilo-title">
    <div class="bo-wrap">
      <header class="ns-section-head">
        <h2 id="ns-profilo-title">Anatomia di un volo suborbitale</h2>
        <p>Dal decollo al ritorno della capsula passano circa dieci o undici minuti in un volo tipico. Dopo lo spegnimento del motore, la capsula percorre un arco balistico e rimane in caduta libera per alcuni minuti attorno all’apogeo.</p>
      </header>

      <ol class="ns-flight-sequence" role="list" aria-label="Fasi e rientri del profilo di volo">
        <li>
          <h3>Decollo</h3>
          <p>Il booster spinge il veicolo con il BE-3PM, alimentato da idrogeno e ossigeno liquidi. La capsula viaggia in cima al razzo.</p>
        </li>
        <li>
          <h3>Separazione e apogeo</h3>
          <p>Terminata la spinta, la capsula si separa e prosegue verso l’apogeo. Il profilo nominale attraversa la linea di Kármán, a 100 km di quota.</p>
        </li>
        <li class="ns-flight-return">
          <h3>Rientri separati</h3>
          <dl>
            <div><dt>Booster</dt><dd>Riaccende il BE-3PM per frenare e atterra in verticale sulla piattaforma.</dd></div>
            <div><dt>Capsula</dt><dd>Rallenta con i paracadute e tocca terra nel deserto del Texas.</dd></div>
          </dl>
        </li>
      </ol>
      <p class="ns-references">
        <a href="https://www.blueorigin.com/new-shepard/experience">Profilo di volo Blue Origin</a>
        <a href="https://www.blueorigin.com/engines/be-3">Scheda del motore BE-3PM</a>
      </p>

      <div class="ns-photo-grid">
        <figure>
          <img src="{booster_photo}" loading="lazy" alt="Il booster di NS-38 frena in verticale sopra la piattaforma con il motore acceso">
          <figcaption>Atterraggio del booster di NS-38.
            <a href="https://www.blueorigin.com/gallery/asset/6972c930c8b28f2654a8abfe">Foto Blue Origin</a>
          </figcaption>
        </figure>
        <figure>
          <img src="{capsule_photo}" loading="lazy" alt="La capsula di NS-38 scende sotto tre paracadute sopra il deserto del Texas">
          <figcaption>Discesa della capsula di NS-38.
            <a href="https://www.blueorigin.com/gallery/asset/6972c92fc8b28f2654a8abe8">Foto Blue Origin</a>
          </figcaption>
        </figure>
      </div>
    </div>
  </section>

  <section class="ns-section ns-timeline-section" id="ns-cronologia" aria-labelledby="ns-cronologia-title">
    <div class="bo-wrap">
      <header class="ns-section-head">
        <h2 id="ns-cronologia-title">Missioni chiave</h2>
        <p>Dai primi tentativi di recupero ai voli con equipaggio e alle prove per la Luna.</p>
      </header>
      <ol class="ns-timeline" role="list">
{timeline}
      </ol>
      <aside class="ns-pause">
        <h3>La pausa del programma</h3>
        <p>Il 30 gennaio 2026 Blue Origin ha annunciato una pausa di almeno due anni per spostare risorse sullo sviluppo dei lander lunari.</p>
        <a class="ns-source" href="https://www.blueorigin.com/news/new-shepard-to-pause-flights">Annuncio di Blue Origin</a>
      </aside>
    </div>
  </section>

  <section class="ns-section" id="ns-ricerca" aria-labelledby="ns-ricerca-title">
    <div class="bo-wrap">
      <header class="ns-section-head">
        <h2 id="ns-ricerca-title">Persone e ricerca</h2>
      </header>
      <div class="ns-use-grid">
        <article class="ns-use">
          <h3>Voli con equipaggio</h3>
          <p>La capsula pressurizzata può ospitare fino a sei persone. Dopo l’ascesa, il tratto in caduta libera dà all’equipaggio il tempo di slacciarsi e osservare la Terra dai finestrini, prima di tornare ai posti per la discesa.</p>
          <a class="ns-record-link" href="{crew_flights}">Voli con equipaggio nell’archivio <span aria-hidden="true">↗</span></a>
          <a class="ns-source" href="https://www.blueorigin.com/new-shepard/fly">La capsula per il volo umano</a>
        </article>
        <article class="ns-use">
          <h3>Esperimenti e dimostrazioni</h3>
          <p>Gli strumenti possono volare dentro la capsula o all’esterno del booster. Su NS-13, un sensore della NASA montato sul booster ha raccolto dati in discesa per provare tecnologie di navigazione e allunaggio di precisione.</p>
          <a class="ns-record-link" href="{research_flights}">Voli di ricerca nell’archivio <span aria-hidden="true">↗</span></a>
          <a class="ns-source" href="https://www.blueorigin.com/news/new-shepard-mission-ns-13-launch-updates">L’esperimento lunare su NS-13</a>
        </article>
      </div>

      <article class="ns-case" id="ns-gravita-lunare" aria-labelledby="ns-case-title">
        <div class="ns-case-copy">
          <p class="ns-context">NS-29</p>
          <h3 id="ns-case-title">Due minuti di gravità lunare simulata</h3>
          <p>Dopo la separazione, piccoli propulsori fanno ruotare la capsula. Gli esperimenti negli alloggiamenti interni avvertono un’accelerazione legata alla rotazione. A circa 11 giri al minuto, il valore previsto al centro degli alloggiamenti è circa un sesto di quello terrestre.</p>
          <p>La prova ha dato ai ricercatori tempo per osservare processi come lo scavo della regolite simulata e il comportamento della polvere in condizioni simili a quelle lunari.</p>
          <a class="ns-record-link" href="{lunar_flight}">Apri NS-29 nell’archivio <span aria-hidden="true">↗</span></a>
          <p class="ns-references">
            <a href="https://www.blueorigin.com/news/new-shepard-ns-29-mission">Risultati di volo Blue Origin</a>
            <a href="https://www.nasa.gov/stmd-flight-opportunities/flight-summaries/lunar-gravity-simulation-via-suborbital-rocket/">Esperimenti sostenuti dalla NASA</a>
          </p>
        </div>
        <dl class="ns-case-stats">
          <div><dt>Giri al minuto</dt><dd>~11</dd></div>
          <div><dt>Carichi a bordo</dt><dd>30</dd></div>
          <div><dt>Tecnologie sostenute da NASA Flight Opportunities</dt><dd>17</dd></div>
        </dl>
      </article>
    </div>
  </section>
</div>
"""


def render_local_page(title, description, body, extra_css="", is_landing=False):
    current = ' aria-current="page"' if is_landing else ""
    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description)}">
  <title>{escape(title)} | Rivoluzione Spaziale</title>
  <link rel="stylesheet" href="portale.css">
  {extra_css}
</head>
<body class="bo-preview">
<header class="topbar">
  <a class="brand" href="{SITE}/index.html">Rivoluzione <span>Spaziale</span></a>
  <nav class="nav" aria-label="Navigazione principale">
    <a href="{SITE}/index.html">Home</a>
    <a href="{SITE}/sezioni/notizie.html">Notizie</a>
    <a href="{SITE}/sezioni/spacex.html">SpaceX</a>
    <a class="active" href="index.html"{current}>Blue Origin</a>
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
    registry = root / "dati.json"
    portal = render_local_page(
        "Blue Origin", "I programmi di Blue Origin e l’archivio dei voli.",
        render_portal(registry, "elenco.html", "new-glenn-ng2.webp"), is_landing=True,
    )
    dossier = render_local_page(
        "New Shepard", NS_DESCRIPTION,
        render_new_shepard(registry, "index.html", "elenco.html", "."),
        extra_css='<link rel="stylesheet" href="new-shepard.css">',
    )
    (root / "index.html").write_text(portal, encoding="utf-8", newline="\n")
    (root / "new-shepard.html").write_text(dossier, encoding="utf-8", newline="\n")
