# Rivoluzione Spaziale

Sito statico multipagina del progetto "Rivoluzione Spaziale".

La home presenta il tema generale della rivoluzione spaziale in atto e collega solo le sezioni principali di primo livello. La sezione SpaceX e gia attiva; le altre pagine sono predisposte come sezioni autonome in costruzione.

Regola di architettura: la navigazione globale e la homepage non devono elencare sottosezioni SpaceX. Lanci imminenti, storico lanci, Starship, Pad di lancio, Localita SpaceX e Storia sono pagine interne alla sezione SpaceX. In futuro potranno esistere sottosezioni equivalenti per altre compagnie, ma non vanno messe nella nav principale.

Tra i dossier SpaceX attivi sono disponibili l'agenda lanci, lo storico Falcon, Starship, la pagina "Pad di lancio", la mappa "Localita SpaceX", la guida pratica "Vedere un lancio da SLC-40" e la sottosezione narrativa "Storia". Questi link devono restare dentro `sezioni/spacex.html`.

`sezioni/guida-lancio-slc40.html` e' una pagina editoriale autonoma, costruita dalla ricerca locale `Guida pratica per vedere un lancio SpaceX da SLC-40 a Cape Canaveral.docx`. Contiene mappa Leaflet, punti di osservazione, logistica, fotografia, sicurezza e fonti operative. Il generatore conserva il suo collegamento nel portale SpaceX ma non ne riscrive il contenuto.

La sottosezione `sezioni/storia-spacex.html` e' un indice di parti storiche selezionabili. La prima parte pubblicata e' "Dalla fondazione fino al primo lancio" e punta a `documenti per sito/fondazione_spacex_fino_primo_falcon1.html`; la seconda e' "Dal primo fallimento al quarto lancio" e punta a `documenti per sito/falcon1_dal_primo_fallimento_al_quarto_lancio.html`; la terza e' "Dal primo successo orbitale al contratto CRS" e punta a `documenti per sito/falcon1_successo_orbitale_contratto_crs.html`. Gli asset comuni sono in `documenti per sito/assets_fondazione/`.

Nota: per aggiornare l'indice Storia SpaceX in modo persistente modificare anche `03_script/genera_sito_rivoluzione.py`, poi rigenerare il sito.

## File principali

- `.gitignore`: tiene fuori da git workbook locali, backup, cache Python, temporanei, bozze Office e output HTML intermedi.
- `index.html`: homepage generale.
- `css/style.css`: stile condiviso.
- `sezioni/`: pagine HTML autonome, incluse SpaceX, Storia SpaceX, lanci imminenti, storico lanci, Starship, pad di lancio e localita SpaceX.
- `pad_di_lancio/`: infografiche e fonti usate dalla pagina dei pad.
- `03_script/genera_sito_rivoluzione.py`: generatore locale che ricostruisce il sito dai dati del progetto.

## Pubblicazione

Il sito pubblico GitHub Pages viene servito dal ramo `gh-pages`. Per rendere visibili online le modifiche al sito, spingere sia `main` sia `main:gh-pages`, poi verificare la URL pubblica con cache-buster.
