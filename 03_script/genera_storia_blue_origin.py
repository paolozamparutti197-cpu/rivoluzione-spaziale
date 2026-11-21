from html import escape


HISTORY_PARTS = (
    (
        "Dai prototipi ai voli suborbitali",
        (
            (
                "le-origini", "2000–2004", "La fondazione e l’idea del riuso",
                "Jeff Bezos, la nascita dell’azienda e le prime scelte sul volo verticale.",
            ),
            (
                "primi-prototipi", "2005–2012", "I primi prototipi",
                "Charon, Goddard e PM2, dalle prove a bassa quota ai test del sistema di fuga.",
            ),
            (
                "new-shepard-atterraggi", "2015–2016", "New Shepard impara a tornare",
                "I primi voli di sviluppo, l’atterraggio verticale e il secondo volo dello stesso booster.",
            ),
            (
                "voli-di-ricerca", "2017–2020", "Dalle prove ai voli di ricerca",
                "La nuova capsula, gli esperimenti in microgravità e la preparazione ai voli con persone.",
            ),
            (
                "primo-equipaggio", "2021", "Il primo equipaggio",
                "La missione NS-16 e l’avvio dei voli suborbitali con passeggeri.",
            ),
            (
                "ns-23-ritorno-e-pausa", "2022–2026", "Da NS-23 alla pausa di New Shepard",
                "Il guasto di NS-23, l’indagine, il ritorno al volo e la sospensione dopo NS-38.",
            ),
        ),
    ),
    (
        "Dai motori all’orbita e alla Luna",
        (
            (
                "be-4-e-new-glenn", "2014–2024", "La costruzione di un lanciatore orbitale",
                "Il motore BE-4, la collaborazione con ULA e lo sviluppo di New Glenn e della rampa LC-36.",
            ),
            (
                "new-glenn-in-orbita", "2025", "New Glenn raggiunge l’orbita",
                "Dal debutto di NG-1 alla missione ESCAPADE e al primo recupero del booster su Jacklyn.",
            ),
            (
                "new-glenn-riuso-e-lc36a", "2026", "Dal primo riuso di New Glenn all’incidente di LC-36A",
                "Il volo NG-3, l’orbita di BlueBird 7 e l’incidente durante la prova a terra a Cape Canaveral.",
            ),
            (
                "blue-moon-e-blue-ring", "Programmi in sviluppo", "Blue Moon e Blue Ring",
                "I lander Mark 1 e Mark 2, il ruolo nel programma Artemis e la logistica in orbita.",
            ),
        ),
    ),
)

HISTORY_INDEX = "storia-blue-origin.html"
HISTORY_DIRECTORY = "storia-blue-origin"
HISTORY_TITLE = "Storia di Blue Origin"
CONSTRUCTION = "In costruzione"


def render_history_index():
    section_number = 1
    sections = []
    for heading, chapters in HISTORY_PARTS:
        items = []
        for slug, period, title, summary in chapters:
            items.append(
                f"""        <li>
          <a class="bo-history-entry" href="{HISTORY_DIRECTORY}/{slug}.html">
            <span class="bo-history-period">{escape(period)}</span>
            <h3>{escape(title)}</h3>
            <p>{escape(summary)}</p>
            <span class="bo-history-status">{CONSTRUCTION}</span>
            <span class="bo-history-arrow" aria-hidden="true">↗</span>
          </a>
        </li>"""
            )
        chapter_items = "\n".join(items)
        sections.append(
            f"""    <section aria-labelledby="capitoli-{section_number}">
      <h2 id="capitoli-{section_number}">{escape(heading)}</h2>
      <ol class="bo-history-list" start="{section_number}">
{chapter_items}
      </ol>
    </section>"""
        )
        section_number += len(chapters)
    part_sections = "\n".join(sections)
    return f"""
<div class="bo-page bo-history">
  <a class="bo-skip" href="#capitoli">Vai all’indice dei capitoli</a>
  <nav class="bo-wrap bo-history-crumb" aria-label="Percorso della pagina">
    <a href="blue-origin.html">Blue Origin</a><span aria-hidden="true">›</span><span aria-current="page">Storia</span>
  </nav>
  <section class="bo-history-heading" aria-labelledby="storia-title">
    <div class="bo-wrap">
      <h1 id="storia-title">{HISTORY_TITLE}</h1>
      <p>Indice del percorso storico, dalla fondazione e dai primi voli di prova a New Glenn e ai programmi lunari.</p>
    </div>
  </section>
  <div class="bo-wrap bo-history-content" id="capitoli" tabindex="-1">
{part_sections}
    <aside class="bo-history-related" aria-labelledby="dossier-title">
      <h2 id="dossier-title">Dossier e archivio dei voli</h2>
      <ul>
        <li><a href="new-shepard.html">New Shepard</a></li>
        <li><a href="new-glenn.html">New Glenn</a></li>
        <li><a href="blue-moon.html">Blue Moon</a></li>
        <li><a href="new-glenn-incidente-lc36.html">Incidente al pad LC-36A</a></li>
        <li><a href="../archivio/blue-origin/elenco.html">Elenco dei lanci</a></li>
      </ul>
    </aside>
  </div>
</div>
"""


def render_history_chapter(chapter, number, previous, following):
    _, period, title, summary = chapter
    navigation = []
    for neighbor, label, relation in (
        (previous, "Capitolo precedente", "prev"),
        (following, "Capitolo successivo", "next"),
    ):
        if neighbor:
            slug, _, neighbor_title, _ = neighbor
            navigation.append(f'''    <a href="{slug}.html" rel="{relation}">
      <span>{label}</span><strong>{escape(neighbor_title)}</strong>
    </a>''')
    navigation_markup = "\n".join(navigation)
    return f"""
<div class="bo-page bo-history bo-history-chapter">
  <nav class="bo-wrap bo-history-crumb" aria-label="Percorso della pagina">
    <a href="../blue-origin.html">Blue Origin</a><span aria-hidden="true">›</span>
    <a href="../{HISTORY_INDEX}">Storia</a><span aria-hidden="true">›</span>
    <span aria-current="page">Capitolo {number}</span>
  </nav>
  <section class="bo-history-heading" aria-labelledby="storia-title">
    <div class="bo-wrap">
      <p class="bo-history-kicker">Capitolo {number} · {escape(period)}</p>
      <h1 id="storia-title">{escape(title)}</h1>
      <p>{escape(summary)}</p>
    </div>
  </section>
  <div class="bo-wrap bo-history-content">
    <span class="bo-history-status">{CONSTRUCTION}</span>
    <div class="bo-actions">
      <a class="bo-button bo-button-quiet" href="../{HISTORY_INDEX}#capitoli">Torna all’indice dei capitoli</a>
    </div>
    <nav class="bo-history-pagination" aria-label="Navigazione tra i capitoli">
{navigation_markup}
    </nav>
  </div>
</div>
"""
