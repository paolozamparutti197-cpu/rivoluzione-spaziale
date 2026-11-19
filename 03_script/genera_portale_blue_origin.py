import json
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote, urlencode

SITE = "https://paolozamparutti197-cpu.github.io/rivoluzione-spaziale"
PHOTO_SOURCE = "https://commons.wikimedia.org/wiki/File:Blue_Origin_New_Glenn_Rocket_Successful_Launch_(9387521).jpg"
NASA_ARTEMIS = "https://www.nasa.gov/missions/artemis/nasas-artemis-iii-mission-to-test-future-moon-lander-operations/"
BO_STYLE_VERSION = "20261119-sfumatura"
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


def blue_origin_styles(directory, *styles):
    return "\n  ".join(
        f'<link rel="stylesheet" href="{directory}{name}.css?v={BO_STYLE_VERSION}">'
        for name in ("blue-origin-theme", *styles)
    )


def render_portal(registry_path, archive_url, photo):
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    flights = data["flights"]
    counts = Counter(flight["program"] for flight in flights)
    latest = max(flights, key=lambda flight: (flight["date"], flight["id"]))
    photo_directory = photo.rpartition("/")[0]
    photo_prefix = f"{photo_directory}/" if photo_directory else ""

    def program_photo(filename, alt, gallery):
        return f"""          <figure class="bo-program-media">
            <img src="{escape(photo_prefix + filename)}" alt="{escape(alt)}" loading="lazy">
            <figcaption><a href="https://www.blueorigin.com/gallery/asset/{gallery}">Foto Blue Origin</a></figcaption>
          </figure>"""

    shepard_photo = program_photo("ns38-lancio.webp", "Il decollo di New Shepard durante NS-38", "6972c92fc8b28f2654a8abf3")
    glenn_photo = program_photo("ng3-lancio.webp", "New Glenn si solleva tra le torri di Cape Canaveral", "69e9395a1532f1a2cfee8e22")
    moon_photo = program_photo("mk1-endurance-camera.webp", "Endurance nella camera termovuoto del Johnson Space Center", "69938aa87f11c19afde0151e")
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
      <a class="bo-latest" href="new-glenn-incidente-lc36.html">
        <span class="bo-latest-label">Dossier New Glenn</span>
        <strong>L’esplosione al pad LC-36A</strong>
        {time_tag("2026-05-28")}
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
{shepard_photo}
          <div class="bo-program-copy">
            <p class="bo-program-context">Suborbitale · Texas</p>
            <h3 id="bo-shepard">New Shepard</h3>
            <p>Da Launch Site One partono voli con persone, esperimenti scientifici e collaudi. La capsula atterra con paracadute e il booster rientra alla base.</p>
            <div class="bo-program-links">
              <a class="bo-program-link" href="new-shepard.html">Dossier New Shepard <span aria-hidden="true">↗</span></a>
              <a class="bo-source" href="{archive_link(archive_url, 'shepard')}">Voli New Shepard</a>
            </div>
          </div>
        </article>
        <article class="bo-program bo-program-glenn" id="new-glenn" aria-labelledby="bo-glenn">
{glenn_photo}
          <div class="bo-program-copy">
            <p class="bo-program-context">Orbitale · Florida</p>
            <h3 id="bo-glenn">New Glenn</h3>
            <p>Il lanciatore pesante parte dal complesso LC-36. Il primo stadio è progettato per atterrare sulla piattaforma Jacklyn, nell’Atlantico.</p>
            <div class="bo-program-links">
              <a class="bo-program-link" href="new-glenn.html">Dossier New Glenn <span aria-hidden="true">↗</span></a>
              <a class="bo-source" href="{archive_link(archive_url, 'glenn')}">Lanci New Glenn</a>
            </div>
          </div>
        </article>
        <article class="bo-program bo-program-moon" id="blue-moon" aria-labelledby="bo-moon">
{moon_photo}
          <div class="bo-program-copy">
            <p class="bo-program-context">Lander lunari</p>
            <h3 id="bo-moon">Blue Moon</h3>
            <p>Mark 1 è il lander per carichi e strumenti scientifici. Mark 2 è progettato per portare astronauti tra l’orbita lunare e la superficie nel programma Artemis.</p>
            <div class="bo-program-links">
              <a class="bo-program-link" href="blue-moon.html">Dossier Blue Moon <span aria-hidden="true">↗</span></a>
              <a class="bo-source" href="{NASA_ARTEMIS}">Blue Moon nel programma Artemis</a>
            </div>
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


NG_DESCRIPTION = (
    "Come vola New Glenn, dai motori del primo stadio al rilascio del carico in orbita, "
    "con gli esiti delle missioni e dei recuperi su Jacklyn."
)
NG_OUTCOMES = {"success": "Orbita prevista raggiunta", "failure": "Orbita prevista mancata"}
NG_RECOVERIES = {"sea": "Atterrato su Jacklyn", "lost": "Booster perso"}
NG_FLIGHT_DETAILS = {
    "NG-1": (
        "Il dimostratore Blue Ring Pathfinder resta fissato al secondo stadio nell’orbita terrestre media prevista.",
        "I motori del primo stadio non si riaccendono per frenare il rientro. Il booster va perso.",
    ),
    "NG-2": (
        "Le due sonde NASA ESCAPADE si separano nella traiettoria di attesa prevista.",
        "Primo atterraggio su Jacklyn. Il booster GS1-2 tornerà a volare su NG-3.",
    ),
    "NG-3": (
        "BlueBird 7 si separa in un’orbita troppo bassa per operare. La FAA riconduce l’anomalia di spinta a una perdita criogenica che ha congelato una linea idraulica.",
        "Il GS1-2, già impiegato per NG-2, atterra su Jacklyn al secondo volo.",
    ),
}
NG_FAA = "https://www.faa.gov/newsroom/statements/general-statements"
NG_NASA = "https://science.nasa.gov/science-research/heliophysics/nasas-escapade-completes-powered-earth-flybys-now-en-route-to-mars/"


def render_glenn_flight(flight, archive_url):
    mission = flight["id"]
    orbital_detail, recovery_detail = NG_FLIGHT_DETAILS.get(mission, (flight["note"], ""))
    outcome = NG_OUTCOMES[flight["outcome"]]
    recovery = NG_RECOVERIES.get(flight["recovery"], "Recupero non indicato")
    outcome_tone = "ng-positive" if flight["outcome"] == "success" else "ng-negative"
    recovery_tone = {"sea": "ng-positive", "lost": "ng-negative"}.get(flight["recovery"], "")
    recovery_copy = f"<p>{escape(recovery_detail)}</p>" if recovery_detail else ""
    return f"""        <li class="ng-mission-row" id="tappa-{escape(mission.lower())}">
          <div class="ng-mission-head">
            <div>
              <p class="ns-mission">{escape(mission)} <span>·</span> {time_tag(flight["date"])}</p>
              <h3>{escape(flight["title"])}</h3>
            </div>
            <a class="ns-record-link" href="{archive_link(archive_url, 'glenn', mission)}"
              aria-label="Apri {escape(mission)} nell’archivio">Archivio {escape(mission)} <span aria-hidden="true">↗</span></a>
          </div>
          <dl class="ng-results">
            <div>
              <dt>Missione orbitale</dt>
              <dd><strong class="{outcome_tone}">{outcome}</strong><p>{escape(orbital_detail)}</p></dd>
            </div>
            <div>
              <dt>Recupero del booster</dt>
              <dd><strong class="{recovery_tone}">{recovery}</strong>{recovery_copy}</dd>
            </div>
          </dl>
        </li>"""


def render_new_glenn(registry_path, portal_url, archive_url, assets_url):
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    flights = sorted(
        (flight for flight in data["flights"] if flight["program"] == "glenn"),
        key=lambda flight: (flight["date"], flight["id"]),
    )
    reached_orbit = sum(flight["outcome"] == "success" for flight in flights)
    landings = sum(flight["recovery"] == "sea" for flight in flights)
    timeline = "\n".join(render_glenn_flight(flight, archive_url) for flight in flights)
    archive = archive_link(archive_url, "glenn")
    launch_photo = escape(assets_url + "/ng3-lancio.webp")
    stage_photo = escape(assets_url + "/ng2-secondo-stadio.webp")
    landing_photo = escape(assets_url + "/ng3-jacklyn.webp")
    return f"""
<div class="bo-page ns-page ng-page">
  <a class="bo-skip" href="#ng-veicolo">Vai alla scheda del razzo</a>
  <div class="bo-wrap ns-breadcrumb">
    <a href="{escape(portal_url)}"><span aria-hidden="true">←</span> Blue Origin</a>
  </div>

  <section class="ns-hero" aria-labelledby="ng-title">
    <div class="bo-wrap ns-hero-grid">
      <div class="ns-hero-copy">
        <p class="ns-context">Lanci orbitali · Florida</p>
        <h1 id="ng-title">New Glenn</h1>
        <p class="ns-lede">Il lanciatore pesante di Blue Origin parte da Cape Canaveral. Il secondo stadio porta il carico in orbita, mentre il booster punta alla piattaforma Jacklyn nell’Atlantico.</p>
        <div class="bo-actions">
          <a class="bo-button" href="#ng-profilo">Segui il profilo di volo <span aria-hidden="true">↓</span></a>
          <a class="bo-button bo-button-quiet" href="{archive}">Archivio New Glenn <span aria-hidden="true">↗</span></a>
        </div>
      </div>
      <figure class="ns-hero-photo">
        <img src="{launch_photo}" width="1760" height="1174" fetchpriority="high"
          alt="New Glenn sale fra le torri di rampa sotto il cielo arancione durante NG-3">
        <figcaption>Decollo di NG-3, 19 aprile 2026.
          <a href="https://www.blueorigin.com/gallery/asset/69e9395a1532f1a2cfee8e22">Foto Blue Origin</a>
        </figcaption>
      </figure>
    </div>
  </section>

  <div class="ns-register">
    <div class="bo-wrap">
      <dl class="ns-register-grid">
        <div><dt>Lanci documentati</dt><dd>{len(flights)}</dd></div>
        <div><dt>Obiettivi orbitali raggiunti</dt><dd>{reached_orbit}</dd></div>
        <div><dt>Atterraggi su Jacklyn</dt><dd>{landings}</dd></div>
      </dl>
      <p>Registro verificato il {time_tag(data["verifiedOn"])}.</p>
    </div>
  </div>

  <nav class="bo-wrap ns-jump" aria-label="Indice del dossier New Glenn">
    <a href="#ng-veicolo">Il razzo</a>
    <a href="#ng-profilo">Profilo di volo</a>
    <a href="#ng-cronologia">Cronologia</a>
    <a href="#ng-escapade">ESCAPADE</a>
  </nav>

  <section class="ns-section" id="ng-veicolo" aria-labelledby="ng-veicolo-title">
    <div class="bo-wrap">
      <header class="ns-section-head">
        <h2 id="ng-veicolo-title">Il razzo a due stadi</h2>
        <p>La configurazione 7×2 impiegata nei primi voli prende il nome dal numero di motori sui due stadi.</p>
      </header>
      <div class="ng-vehicle-grid">
        <article class="ns-use">
          <h3>Primo stadio · 7 BE-4</h3>
          <p>Sette motori alimentati da gas naturale liquefatto e ossigeno liquido sollevano il razzo. Il booster è progettato per rientrare e volare di nuovo.</p>
        </article>
        <article class="ns-use">
          <h3>Secondo stadio · 2 BE-3U</h3>
          <p>Due motori riaccendibili, a idrogeno e ossigeno liquidi, regolano la traiettoria per raggiungere l’orbita di rilascio.</p>
        </article>
        <article class="ns-use">
          <h3>Carenatura · 7 metri</h3>
          <p>La carenatura protegge satelliti e sonde durante l’ascesa. Le due metà si separano quando la protezione aerodinamica ha esaurito la sua funzione.</p>
        </article>
      </div>
      <p class="ns-references">
        <a href="https://www.blueorigin.com/new-glenn">Scheda del lanciatore</a>
        <a href="https://www.blueorigin.com/engines">Scheda dei motori</a>
      </p>
      <p class="ng-variants">Blue Origin ha presentato anche la variante 9×4 e lo stadio aggiuntivo GS3 per le missioni ad alta energia.
        <a href="https://www.blueorigin.com/news/new-glenn-expands-reach-with-gs3">Sviluppo di GS3</a>
      </p>
    </div>
  </section>

  <section class="ns-section ng-profile" id="ng-profilo" aria-labelledby="ng-profilo-title">
    <div class="bo-wrap">
      <header class="ns-section-head">
        <h2 id="ng-profilo-title">Dal decollo a due traiettorie</h2>
        <p>Con la separazione degli stadi iniziano in parallelo l’inserimento orbitale e il rientro del booster.</p>
      </header>
      <div class="ng-flight-start">
        <h3>Decollo e separazione</h3>
        <p>I BE-4 si accendono a LC-36. Al termine della spinta del primo stadio, i due stadi si separano.</p>
      </div>
      <div class="ns-photo-grid ng-flight-branches">
        <article class="ng-branch" aria-labelledby="ng-orbita-title">
          <div class="ng-branch-copy">
            <h3 id="ng-orbita-title">Secondo stadio · verso l’orbita</h3>
            <ol>
              <li>I BE-3U si accendono e proseguono l’ascesa. La carenatura si apre e si separa.</li>
              <li>Il secondo stadio raggiunge la traiettoria prevista e rilascia il carico secondo il piano di missione.</li>
            </ol>
          </div>
          <figure>
            <img src="{stage_photo}" width="1360" height="907" loading="lazy"
              alt="Ugelli BE-3U del secondo stadio con la Terra sullo sfondo durante NG-2">
            <figcaption>Secondo stadio durante NG-2.
              <a href="https://www.blueorigin.com/gallery/asset/6931c2fe1b7576ab9bbd8c75">Foto Blue Origin</a>
            </figcaption>
          </figure>
        </article>
        <article class="ng-branch" aria-labelledby="ng-rientro-title">
          <div class="ng-branch-copy">
            <h3 id="ng-rientro-title">Primo stadio · verso Jacklyn</h3>
            <ol>
              <li>Il booster orienta e frena la discesa verso la piattaforma già posizionata nell’Atlantico.</li>
              <li>I motori frenano la parte finale della discesa. Le gambe di atterraggio sostengono il booster sul ponte.</li>
            </ol>
          </div>
          <figure>
            <img src="{landing_photo}" width="1400" height="788" loading="lazy"
              alt="Primo stadio di New Glenn in verticale sulla piattaforma Jacklyn dopo NG-3">
            <figcaption>Booster GS1-2 su Jacklyn dopo NG-3.
              <a href="https://www.blueorigin.com/gallery/asset/69ea2155454dd5737948911f">Foto Blue Origin</a>
            </figcaption>
          </figure>
        </article>
      </div>
      <p class="ns-references"><a href="https://www.blueorigin.com/missions/ng-3">Profilo di volo e webcast NG-3</a></p>
    </div>
  </section>

  <section class="ns-section ns-timeline-section" id="ng-cronologia" aria-labelledby="ng-cronologia-title">
    <div class="bo-wrap">
      <header class="ns-section-head">
        <h2 id="ng-cronologia-title">Cronologia dei lanci</h2>
      </header>
      <ol class="ns-timeline ng-timeline">
{timeline}
      </ol>
      <p class="ns-references">
        <a href="{NG_FAA}">Indagini FAA su NG-1 e NG-3</a>
        <a href="https://www.sec.gov/Archives/edgar/data/1780312/000119312526453759/asts-20260930.htm">AST SpaceMobile · BlueBird 7</a>
      </p>
      <aside class="ns-pause" aria-labelledby="ng-hotfire">
        <h3 id="ng-hotfire">28 maggio 2026 · La prova a terra</h3>
        <p>Un’esplosione durante l’accensione statica distrusse il veicolo preparato per il quarto volo e danneggiò la rampa LC-36A.</p>
        <a class="ns-source" href="new-glenn-incidente-lc36.html">Il dossier sull’esplosione a LC-36A</a>
      </aside>
    </div>
  </section>

  <section class="ns-section" id="ng-escapade" aria-labelledby="ng-escapade-title">
    <div class="bo-wrap">
      <article class="ns-case ng-case">
        <div class="ns-case-copy">
          <p class="ns-context">NG-2 · NASA</p>
          <h2 id="ng-escapade-title">ESCAPADE, un anno di attesa per Marte</h2>
          <p>NG-2 ha rilasciato due sonde su una traiettoria di attesa vicino alla Terra. Nel novembre 2026 entrambe hanno combinato un passaggio ravvicinato alla Terra e un’accensione dei propri motori per dirigersi verso Marte.</p>
          <p>Studieranno come il vento solare interagisce con l’ambiente marziano e contribuisce alla perdita di atmosfera.</p>
          <p class="ns-references"><a href="{NG_NASA}">NASA · I sorvoli della Terra</a></p>
        </div>
        <p class="ng-case-link">
          <a class="ns-record-link" href="{archive_link(archive_url, 'glenn', 'NG-2')}">Apri NG-2 nell’archivio <span aria-hidden="true">↗</span></a>
        </p>
      </article>
    </div>
  </section>
</div>
"""


BM_DESCRIPTION = (
    "I lander lunari Blue Moon Mark 1 e Mark 2, dal lancio con New Glenn all’allunaggio, "
    "con le prove a terra e le missioni annunciate da NASA e Blue Origin."
)
BM_PROGRAM = "https://www.blueorigin.com/blue-moon"
BM_MARK_1 = f"{BM_PROGRAM}/mark-1"
BM_NASA_MK1 = "https://www.nasa.gov/event/clps-flight-blue-origins-blue-moon-mark-1/"
BM_NASA_HLS = "https://www.nasa.gov/missions/artemis/nasa-partners-accelerate-lander-development-for-2028-moon-missions/"

BM_TESTS = (
    (
        "2026-05-04", "MK1", "Prove ambientali di Endurance",
        "NASA ha annunciato il completamento delle prove nella camera termovuoto A di Houston, "
        "dove sono state riprodotte le condizioni di vuoto e temperatura previste in missione.",
        "https://www.nasa.gov/missions/artemis/blue-origin-moon-lander-completes-testing-at-nasa-vacuum-chamber/",
        "NASA · Le prove in camera A",
    ),
    (
        "2026-05-07", "MK2", "Cabina per le simulazioni",
        "NASA ha reso operativo a Houston il modello di cabina a grandezza naturale per addestramento e prove "
        "di procedure con equipaggio.",
        "https://www.nasa.gov/directorates/esdmd/artemis-campaign-development-division/human-landing-system-program/industry-moon-lander-training-cabin-lands-at-nasa-for-artemis/",
        "NASA · Il modello della cabina",
    ),
    (
        "2026-08", "MK1", "Comunicazioni di Endurance",
        "NASA ha confermato il completamento delle verifiche di comunicazione con la rete di satelliti TDRS "
        "e con la Deep Space Network.",
        "https://www.nasa.gov/missions/moon-base/nasa-provides-updates-on-moon-base-cargo-landers-tech-demonstrations/",
        "NASA · Aggiornamento sui collaudi",
    ),
)
BM_MISSIONS = (
    (
        "2027", "MK1", "Endurance · Moon Base I",
        "Il primo Mark 1 tenterà un allunaggio a Shackleton Connecting Ridge, nella regione "
        "del polo sud lunare. Il calendario NASA indica il 2027.",
        BM_NASA_MK1, "NASA · Calendario di Endurance",
    ),
    (
        "2027", "MK2", "Artemis III · Prova in orbita terrestre",
        "Orion si avvicinerà e si aggancerà a un veicolo di prova del Mark 2 in orbita terrestre bassa. "
        "Gli astronauti entreranno nel veicolo per valutare cabina, comandi e sistemi di supporto vitale.",
        NASA_ARTEMIS, "NASA · Profilo di Artemis III",
    ),
    (
        "Fine 2027", "MK1", "VIPER · Il rover per il polo sud",
        "La pianificazione NASA prevede la consegna di VIPER con un secondo Mark 1. Il rover cercherà ghiaccio "
        "d’acqua nelle zone in ombra permanente vicine al polo sud.",
        "https://www.nasa.gov/news-release/nasa-selects-blue-origin-to-deliver-viper-rover-to-moons-south-pole/",
        "NASA · La consegna di VIPER",
    ),
    (
        "Prima del volo con equipaggio", "MK2", "Dimostrazione lunare senza equipaggio",
        "NASA richiede una dimostrazione senza astronauti prima dei voli con equipaggio. Blue Origin prevede "
        "di provare l’intero profilo del Mark 2 con i suoi stadi di trasferimento.",
        BM_NASA_HLS, "NASA · La dimostrazione prevista",
    ),
    (
        "2028", "Obiettivo NASA", "Artemis IV · Primo allunaggio del programma",
        "NASA punta alla regione del polo sud lunare. Sceglierà il lander in base alla preparazione dei "
        "veicoli e all’esito delle prove.",
        BM_NASA_HLS, "NASA · Preparazione all’allunaggio",
    ),
)


def render_moon_milestones(rows, planned=False):
    def date_markup(value):
        if planned:
            return escape(value)
        if len(value) == 7:
            return f'<time datetime="{value}">{MONTHS[int(value[5:]) - 1]} {value[:4]}</time>'
        return time_tag(value)

    return "\n".join(
        f"""        <li class="bm-milestone">
          <p class="bm-milestone-date">{date_markup(when)} <span aria-hidden="true">·</span> {label}</p>
          <h4>{escape(title)}</h4>
          <p>{escape(detail)}</p>
          <a class="ns-source" href="{escape(source)}">{escape(source_label)}</a>
        </li>"""
        for when, label, title, detail, source, source_label in rows
    )


def render_blue_moon(portal_url, assets_url):
    chamber = escape(assets_url + "/mk1-endurance-camera.webp")
    mark_1 = escape(assets_url + "/blue-moon-mark-1.webp")
    mark_2 = escape(assets_url + "/blue-moon-mark-2.webp")
    tests = render_moon_milestones(BM_TESTS)
    missions = render_moon_milestones(BM_MISSIONS, planned=True)
    return f"""
<div class="bo-page ns-page bm-page">
  <a class="bo-skip" href="#bm-lander">Vai al confronto tra i lander</a>
  <div class="bo-wrap ns-breadcrumb">
    <a href="{escape(portal_url)}"><span aria-hidden="true">←</span> Blue Origin</a>
  </div>

  <section class="ns-hero" aria-labelledby="bm-title">
    <div class="bo-wrap ns-hero-grid">
      <div class="ns-hero-copy">
        <p class="ns-context">Lander lunari · Blue Origin</p>
        <h1 id="bm-title">Blue Moon</h1>
        <p class="ns-lede">Mark 1 è progettato per consegnare carichi sulla Luna. Mark 2, nella versione con equipaggio, porterà astronauti tra Orion in orbita lunare e la superficie.</p>
        <div class="bo-actions">
          <a class="bo-button" href="#bm-lander">Confronta i lander <span aria-hidden="true">↓</span></a>
          <a class="bo-button bo-button-quiet" href="#bm-cronologia">Segui le missioni <span aria-hidden="true">↓</span></a>
        </div>
      </div>
      <figure class="ns-hero-photo">
        <img src="{chamber}" width="1680" height="1120" fetchpriority="high"
          alt="Il lander Endurance nella camera termovuoto del Johnson Space Center">
        <figcaption>Endurance nella camera termovuoto A della NASA, 12 febbraio 2026.
          <a href="https://www.blueorigin.com/gallery/asset/69938aa87f11c19afde0151e">Foto Blue Origin</a>
        </figcaption>
      </figure>
    </div>
  </section>

  <nav class="bo-wrap ns-jump" aria-label="Indice del dossier Blue Moon">
    <a href="#bm-lander">Mark 1 e Mark 2</a>
    <a href="#bm-profilo">Dalla Terra alla Luna</a>
    <a href="#bm-cronologia">Prove e missioni</a>
  </nav>

  <section class="ns-section" id="bm-lander" aria-labelledby="bm-lander-title">
    <div class="bo-wrap">
      <header class="ns-section-head">
        <h2 id="bm-lander-title">Mark 1 e Mark 2</h2>
      </header>
      <div class="bm-lander-grid">
        <article class="bm-lander" aria-labelledby="bm-mark-1">
          <figure>
            <img src="{mark_1}" width="1280" height="853" loading="lazy"
              alt="Illustrazione di Mark 1 con la piattaforma di carico e la Terra sopra l’orizzonte lunare">
            <figcaption><a href="{BM_PROGRAM}">Illustrazione di progetto · Blue Origin</a></figcaption>
          </figure>
          <div class="bm-lander-copy">
            <h3 id="bm-mark-1">Mark 1 · Cargo</h3>
            <dl class="bm-specs">
              <div><dt>Compito</dt><dd>Consegnare strumenti, rover e attrezzature sulla superficie.</dd></div>
              <div><dt>Lancio</dt><dd>Un New Glenn. Blue Origin indica fino a 3 tonnellate di carico nella configurazione 7×2.</dd></div>
              <div><dt>Propulsione</dt><dd>Un motore BE-7 riaccendibile, a idrogeno e ossigeno liquidi.</dd></div>
            </dl>
            <a class="ns-source" href="{BM_MARK_1}">Blue Origin · Scheda Mark 1</a>
          </div>
        </article>
        <article class="bm-lander" aria-labelledby="bm-mark-2">
          <figure>
            <img src="{mark_2}" width="1280" height="853" loading="lazy"
              alt="Illustrazione di Mark 2 sulla Luna con cabina, scala e astronauta accanto al lander">
            <figcaption><a href="{BM_PROGRAM}">Illustrazione di progetto · Blue Origin</a></figcaption>
          </figure>
          <div class="bm-lander-copy">
            <h3 id="bm-mark-2">Mark 2 · Equipaggio</h3>
            <dl class="bm-specs">
              <div><dt>Compito</dt><dd>Far scendere gli astronauti sulla Luna e riportarli a Orion in orbita lunare.</dd></div>
              <div><dt>Lancio</dt><dd>Il lander parte senza equipaggio su New Glenn. Gli astronauti partono su SLS a bordo di Orion.</dd></div>
              <div><dt>Cabina</dt><dd>Nel profilo iniziale descritto da NASA, due astronauti passano al lander e gli altri due restano su Orion.</dd></div>
            </dl>
            <a class="ns-source" href="{BM_NASA_HLS}">NASA · Il profilo con equipaggio</a>
          </div>
        </article>
      </div>
    </div>
  </section>

  <section class="ns-section bm-profile" id="bm-profilo" aria-labelledby="bm-profilo-title">
    <div class="bo-wrap">
      <header class="ns-section-head">
        <h2 id="bm-profilo-title">Dalla Terra alla Luna</h2>
        <p>New Glenn lancia i lander. Il percorso successivo cambia con il tipo di missione.</p>
      </header>
      <div class="bm-route-grid">
        <article class="bm-route">
          <h3>Mark 1 · Missione cargo</h3>
          <ol>
            <li><strong>Partenza.</strong> Un New Glenn lancia il lander con il carico già installato.</li>
            <li><strong>Trasferimento.</strong> Dopo la separazione dal lanciatore, il lander prosegue verso la Luna, guidato dai suoi sistemi di navigazione.</li>
            <li><strong>Discesa.</strong> Il BE-7 modula la spinta per frenare e il lander usa la navigazione autonoma per puntare al sito previsto.</li>
            <li><strong>Superficie.</strong> Endurance proverà le tecnologie di allunaggio e porterà strumenti scientifici della NASA.</li>
          </ol>
        </article>
        <article class="bm-route">
          <h3>Mark 2 Alpha · Profilo lunare proposto</h3>
          <ol>
            <li><strong>Partenza.</strong> Il lander e tre stadi di trasferimento vengono lanciati separatamente e si agganciano in orbita terrestre.</li>
            <li><strong>Trasferimento.</strong> Gli stadi spingono il lander fino a un’orbita polare ellittica attorno alla Luna e si separano man mano.</li>
            <li><strong>Discesa.</strong> Orion raggiunge il lander in orbita lunare. Due astronauti si trasferiscono su Mark 2 e scendono verso la regione del polo sud.</li>
            <li><strong>Ritorno.</strong> Il lander risale verso Orion dopo le operazioni sulla superficie. Il viaggio di ritorno a Terra avviene su Orion.</li>
          </ol>
        </article>
      </div>
      <p class="ns-references">
        <a href="new-glenn.html">Dossier New Glenn</a>
        <a href="{BM_MARK_1}">Blue Origin · Missione Mark 1</a>
        <a href="{BM_NASA_HLS}">NASA · Profilo Mark 2 Alpha</a>
      </p>
      <aside class="ns-pause" aria-labelledby="bm-endurance-title">
        <h3 id="bm-endurance-title">Che cosa misurerà Endurance</h3>
        <p>Le telecamere SCALPSS osserveranno come il getto del motore solleva la polvere durante la discesa. Il retroriflettore laser resterà sulla superficie come riferimento per le misure di posizione.</p>
        <a class="ns-source" href="{BM_NASA_MK1}">NASA · Gli strumenti di Endurance</a>
      </aside>
    </div>
  </section>

  <section class="ns-section ns-timeline-section" id="bm-cronologia" aria-labelledby="bm-cronologia-title">
    <div class="bo-wrap">
      <header class="ns-section-head">
        <h2 id="bm-cronologia-title">Dalle prove alle missioni</h2>
        <p>Stato verificato il {time_tag("2026-11-17")}. Le date di volo seguono la pianificazione pubblica della NASA.</p>
      </header>
      <div class="bm-timeline-grid">
        <section class="bm-timeline" aria-labelledby="bm-tests-title">
          <h3 id="bm-tests-title">Prove completate a terra</h3>
          <ol>
{tests}
          </ol>
        </section>
        <section class="bm-timeline bm-timeline-planned" aria-labelledby="bm-missions-title">
          <h3 id="bm-missions-title">Missioni annunciate</h3>
          <ol>
{missions}
          </ol>
        </section>
      </div>
    </div>
  </section>
</div>
"""


LC36_TITLE = "New Glenn, l’esplosione al pad LC-36A"
LC36_DESCRIPTION = (
    "Il collaudo del 28 maggio 2026 a Cape Canaveral, i danni al pad di New Glenn, "
    "l’indagine sulla valvola del BE-4 e il piano di ricostruzione."
)
LC36_INVESTIGATION = "https://www.blueorigin.com/news/gs1-3-hotfire-updates"
LC36_REBUILD = "https://www.blueorigin.com/news/new-glenn-return-to-flight"
LC36_RANGE = "https://www.dvidshub.net/news/566396/space-launch-delta-45-remains-go-launch"
LC36_REPORTAGE = "https://spaceflightnow.com/2026/05/29/blue-origins-new-glenn-rocket-explodes-during-prelaunch-testing-at-cape-canaveral/"
LC36_VIDEO_ID = "1O90WZJALYc"
LC36_NASA_PHOTO = "https://images-assets.nasa.gov/image/NHQ20260529_admin_0004/NHQ20260529_admin_0004~orig.jpg"
LC36_BEFORE_PHOTO = "https://www.blueorigin.com/gallery/asset/69de4248c29fe8ac1037fdc6"
LC36_FAA_EA = "https://www.faa.gov/space/stakeholderengagement/blue-origin-new-glenn"
LC36_REUTERS = "https://www.reuters.com/science/blue-origin-delays-new-glenn-rocket-launch-into-january-ft-reports-2026-11-05/"


def render_lc36_dossier(portal_url, assets_url, embed_video=True):
    after_photo = escape(assets_url + "/lc36-29-maggio-2026.webp")
    before_photo = escape(assets_url + "/lc36-13-aprile-2026.webp")
    player = f"""
            <iframe src="https://www.youtube-nocookie.com/embed/{LC36_VIDEO_ID}"
              title="L’esplosione di New Glenn a LC-36A ripresa da Spaceflight Now"
              aria-describedby="lc-video-caption" loading="lazy"
              style="display:block;width:100%;height:auto;min-height:200px;aspect-ratio:16/9;border:0"
              referrerpolicy="strict-origin-when-cross-origin"
              allow="encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>""" if embed_video else ""
    return f"""
<div class="bo-page ns-page lc-page">
  <a class="bo-skip" href="#lc-incident">Vai all’articolo</a>
  <div class="bo-wrap ns-breadcrumb">
    <a href="{escape(portal_url)}"><span aria-hidden="true">←</span> Blue Origin</a>
    <a href="new-glenn.html">New Glenn <span aria-hidden="true">↗</span></a>
  </div>
  <article aria-labelledby="lc-title">
    <header class="lc-header">
      <div class="bo-wrap lc-head-grid">
        <div class="lc-intro">
          <p class="ns-context">28 maggio 2026 · Cape Canaveral, Florida</p>
          <h1 id="lc-title">{LC36_TITLE}</h1>
          <p class="ns-lede">Un’accensione di prova distrusse il razzo preparato per NG-4 e danneggiò il suo pad. La ricostruzione di quella sera, dell’indagine sul BE-4 e del lavoro necessario per tornare al volo.</p>
          <p class="lc-verified">Aggiornato al {time_tag("2026-11-17")}</p>
        </div>
        <figure class="lc-photo">
          <div class="lc-aerial">
            <img src="{after_photo}" width="2320" height="1547" fetchpriority="high"
              alt="Il complesso LC-36 dopo l’esplosione, visto dall’elicottero durante il sorvolo della NASA">
          </div>
          <figcaption>LC-36 durante il sorvolo del 29 maggio, il giorno dopo l’esplosione.
            <a href="{LC36_NASA_PHOTO}">Dettaglio della foto NASA / John Kraus</a>
          </figcaption>
        </figure>
      </div>
    </header>

    <div class="bo-wrap lc-layout">
      <nav class="lc-index" aria-label="Indice del dossier">
        <a href="#lc-incident">Il collaudo</a>
        <a href="#lc-indagine">L’indagine sul BE-4</a>
        <a href="#lc-danni">I danni al pad</a>
        <a href="#lc-ricostruzione">La ricostruzione</a>
        <a href="#lc-ripresa">Le missioni in attesa</a>
      </nav>

      <div class="lc-story">
        <section id="lc-incident" aria-labelledby="lc-incident-title">
          <h2 id="lc-incident-title">L’esplosione durante il collaudo</h2>
          <p>Verso le 21:00 del 28 maggio in Florida, le 03:00 del 29 maggio in Italia, il New Glenn era sulla rampa LC-36A per un’accensione statica. I due stadi erano assemblati e il razzo era trattenuto alla base. Il collaudo serviva a verificare l’avvio dei motori insieme ai sistemi del veicolo e della rampa in condizioni simili a quelle di una partenza.</p>
          <p>Durante il test, un’esplosione distrusse il veicolo, compreso il nuovo primo stadio GS1-3. Blue Origin confermò di aver rintracciato tutto il personale. La Space Force intervenne durante la notte. Meno di dodici ore dopo, lo stesso poligono gestì un lancio di Falcon 9 da un’altra rampa. Blue Origin avvisò anche che frammenti del razzo avrebbero potuto raggiungere la costa.</p>
          <figure class="lc-photo lc-archive-photo" id="lc-video">{player}
            <figcaption id="lc-video-caption">Il momento dell’esplosione, 28 maggio 2026. Riprese di Adam Bernstein e John Pisani, Spaceflight Now.
              <a href="https://www.youtube.com/watch?v={LC36_VIDEO_ID}">Guarda il video originale su YouTube</a>
            </figcaption>
          </figure>
          <p>Per il quarto lancio, Blue Origin aveva annunciato 48 satelliti Amazon Leo, destinati all’orbita bassa. Al momento dell’esplosione i satelliti erano ancora presso l’impianto di preparazione del carico, secondo la ricostruzione di Spaceflight Now.</p>
          <p class="ns-references">
            <a href="{LC36_RANGE}">Space Launch Delta 45 · Resoconto dell’intervento</a>
            <a href="{LC36_INVESTIGATION}">Blue Origin · Comunicati del 28 e 29 maggio</a>
            <a href="https://www.linkedin.com/posts/blue-origin_launch-alert-new-glenns-fourth-launch-activity-7465443417045688323--DKM">Blue Origin · Annuncio di NG-4</a>
            <a href="{LC36_REPORTAGE}">Spaceflight Now · Riprese e resoconto</a>
          </p>
        </section>

        <section id="lc-indagine" aria-labelledby="lc-indagine-title">
          <h2 id="lc-indagine-title">Come si è arrivati alla valvola</h2>
          <p>Il 30 giugno Blue Origin indicò la parte posteriore del primo stadio come area di origine. Su New Glenn 7×2, quella sezione ospita sette BE-4. Ogni motore usa gas naturale liquefatto come combustibile e ossigeno liquido come ossidante. La valvola principale dell’ossigeno regola l’ammissione dell’ossidante al motore.</p>
          <ol class="lc-findings">
            <li>
              <span>{time_tag("2026-08-05")}</span>
              <p>Blue Origin localizzò l’origine dell’anomalia nella valvola principale dell’ossigeno di uno dei BE-4. L’ispezione dei componenti recuperati confermò quella localizzazione. L’azienda condusse prove sui singoli componenti e accensioni al banco per capire il guasto e verificare le modifiche.</p>
            </li>
            <li>
              <span>{time_tag("2026-11-10")}</span>
              <p>La versione modificata della valvola superò le prove di qualificazione. Blue Origin dichiarò di averla già installata sui motori destinati ai prossimi voli e di aver avviato l’aggiornamento del resto della flotta. L’obiettivo comunicato era chiudere l’indagine entro novembre.</p>
            </li>
          </ol>
          <p>Al 17 novembre, il meccanismo del guasto interno e la sequenza completa dell’esplosione restavano senza una ricostruzione pubblica.</p>
          <p class="ns-references">
            <a href="{LC36_INVESTIGATION}">Blue Origin · Aggiornamenti dell’indagine GS1-3</a>
            <a href="{LC36_REBUILD}">Blue Origin · Ricostruzione preliminare di giugno</a>
            <a href="https://www.blueorigin.com/engines">Blue Origin · Scheda del BE-4</a>
          </p>
          <aside class="ns-pause" aria-labelledby="lc-ng3">
            <h3 id="lc-ng3">Il precedente di NG-3</h3>
            <p>Nel volo del 19 aprile, una perdita criogenica congelò una linea idraulica del secondo stadio prima di un’anomalia di spinta. La FAA chiuse quell’indagine il 22 maggio. Sul collaudo del 28 maggio, l’agenzia precisò a Spaceflight Now che la prova a terra era fuori dal perimetro delle attività coperte dalla licenza FAA.</p>
            <p class="ns-references">
              <a href="{NG_FAA}">FAA · Conclusioni su NG-3</a>
              <a href="{LC36_REPORTAGE}">Spaceflight Now · Risposta FAA sul collaudo</a>
            </p>
          </aside>
        </section>

        <section id="lc-danni" aria-labelledby="lc-danni-title">
          <h2 id="lc-danni-title">Che cosa rimase della rampa</h2>
          <p>Nel bilancio del 30 giugno Blue Origin indicò la perdita di una torre parafulmine, del trasportatore che sollevava il razzo in verticale e dei cilindri idraulici. La torre di servizio del veicolo aveva danni riparabili. Rimasero utilizzabili il parco serbatoi, la torre dell’acqua e l’edificio di integrazione.</p>
          <p>Nell’edificio c’erano tre secondi stadi e il booster <i>Never Tell Me The Odds</i>, già usato su NG-2 e NG-3. Blue Origin trasferì quei mezzi mentre rimuoveva i detriti e recuperava componenti sul pad. A fine giugno dichiarò concluse le operazioni di recupero e sgombero.</p>
          <p class="ns-references"><a href="{LC36_REBUILD}">Blue Origin · Bilancio dei danni e recupero</a></p>
          <figure class="lc-photo lc-archive-photo">
            <img src="{before_photo}" width="1400" height="933" loading="lazy"
              alt="New Glenn in verticale tra le torri del complesso LC-36 prima della missione NG-3">
            <figcaption>LC-36 prima dell’incidente. New Glenn sulla rampa per NG-3, 13 aprile 2026.
              <a href="{LC36_BEFORE_PHOTO}">Foto Blue Origin</a>
            </figcaption>
          </figure>
        </section>

        <section id="lc-ricostruzione" aria-labelledby="lc-ricostruzione-title">
          <h2 id="lc-ricostruzione-title">Come cambia il lavoro al pad</h2>
          <p>L’azienda ha anticipato per LC-36A una procedura che stava già sviluppando per il secondo pad. L’assemblaggio dei due stadi resta orizzontale nell’edificio di integrazione. La movimentazione sulla rampa cambia in tre passaggi.</p>
          <ol class="lc-steps">
            <li><strong>Trasporto.</strong> Il veicolo assemblato raggiunge la rampa in orizzontale.</li>
            <li><strong>Sollevamento.</strong> Una gru lo ruota e lo posa sulla piattaforma di lancio. I collegamenti dalla torre vengono agganciati al veicolo.</li>
            <li><strong>Carico.</strong> Il carico viene installato in cima al razzo già in verticale.</li>
          </ol>
          <p>In agosto Blue Origin ha annunciato i lavori di LC-36B, previsto per la variante 9×4. LC-36A resta destinato al 7×2. Intanto la FAA ha pubblicato una bozza di valutazione ambientale per la proposta di passare da 12 a un massimo di 50 lanci annuali a LC-36A.</p>
          <p class="ns-references">
            <a href="{LC36_REBUILD}">Blue Origin · Procedura di integrazione</a>
            <a href="https://www.blueorigin.com/news/returning-launch-complex-36-to-two-pads">Blue Origin · Il secondo pad</a>
            <a href="{LC36_FAA_EA}">FAA · Valutazione ambientale</a>
          </p>
        </section>

        <section id="lc-ripresa" aria-labelledby="lc-ripresa-title">
          <h2 id="lc-ripresa-title">Il ritorno al volo e le missioni in attesa</h2>
          <p>A giugno il piano di Blue Origin puntava a un rientro entro la fine del 2026. Nell’aggiornamento del 16 ottobre l’azienda dava ancora LC-36A in ripristino. Il 5 novembre Reuters ha riferito di un obiettivo interno per gennaio 2027, sulla base di un memo aziendale consultato dall’agenzia. L’aggiornamento pubblico del 10 novembre riguarda la qualificazione della valvola e la chiusura dell’indagine.</p>
          <p>Il ritorno al volo interessa anche il programma lunare. Il calendario NASA indica il 2027 per Endurance, il primo Blue Moon Mark 1. Sempre nel 2027, Artemis III prevede una prova di aggancio fra Orion e un veicolo di test del Mark 2 in orbita terrestre. La preparazione del lanciatore e quella dei due lander procedono come collaudi distinti.</p>
          <p class="ns-references">
            <a href="https://www.blueorigin.com/news/building-infrastructure-for-more-frequent-launches-in-florida">Blue Origin · Aggiornamento del 16 ottobre</a>
            <a href="{LC36_REUTERS}">Reuters · Il memo sul ritorno al volo</a>
            <a href="{BM_NASA_MK1}">NASA · Calendario di Endurance</a>
            <a href="{NASA_ARTEMIS}">NASA · Profilo di Artemis III</a>
          </p>
          <p class="lc-related">
            <a class="ns-record-link" href="new-glenn.html">Dossier New Glenn <span aria-hidden="true">↗</span></a>
            <a class="ns-record-link" href="blue-moon.html">Dossier Blue Moon <span aria-hidden="true">↗</span></a>
          </p>
        </section>
      </div>
    </div>
  </article>
</div>
"""


def render_local_page(title, description, body, styles=(), is_landing=False):
    current = ' aria-current="page"' if is_landing else ""
    return f"""<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description)}">
  <title>{escape(title)} | Rivoluzione Spaziale</title>
  {blue_origin_styles("", "portale", *styles)}
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
        styles=("new-shepard",),
    )
    glenn = render_local_page(
        "New Glenn", NG_DESCRIPTION,
        render_new_glenn(registry, "index.html", "elenco.html", "."),
        styles=("new-shepard", "new-glenn"),
    )
    moon = render_local_page(
        "Blue Moon", BM_DESCRIPTION,
        render_blue_moon("index.html", "."),
        styles=("new-shepard", "blue-moon"),
    )
    incident = render_local_page(
        LC36_TITLE, LC36_DESCRIPTION,
        render_lc36_dossier("index.html", ".", embed_video=False),
        styles=("new-shepard", "incidente-lc36"),
    )
    (root / "index.html").write_text(portal, encoding="utf-8", newline="\n")
    (root / "new-shepard.html").write_text(dossier, encoding="utf-8", newline="\n")
    (root / "new-glenn.html").write_text(glenn, encoding="utf-8", newline="\n")
    (root / "blue-moon.html").write_text(moon, encoding="utf-8", newline="\n")
    (root / "new-glenn-incidente-lc36.html").write_text(incident, encoding="utf-8", newline="\n")
