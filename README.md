# Rivoluzione Spaziale

Sito statico multipagina del progetto "Rivoluzione Spaziale".

La home presenta il tema generale della rivoluzione spaziale in atto e collega solo le sezioni principali di primo livello. La sezione SpaceX e gia attiva; le altre pagine sono predisposte come sezioni autonome in costruzione.

Regola di architettura: la navigazione globale e la homepage non devono elencare sottosezioni SpaceX. Lanci imminenti, storico lanci, Starship, Pad di lancio e Storia sono pagine interne alla sezione SpaceX. In futuro potranno esistere sottosezioni equivalenti per altre compagnie, ma non vanno messe nella nav principale.

Tra i dossier SpaceX attivi sono disponibili l'agenda lanci, lo storico Falcon, Starship, la pagina "Pad di lancio" e la sottosezione narrativa "Storia". Questi link devono restare dentro `sezioni/spacex.html`.

La sottosezione `sezioni/storia-spacex.html` e' un indice di parti storiche selezionabili. La prima parte pubblicata e' "Dalla fondazione fino al primo lancio" e punta a `documenti per sito/fondazione_spacex_fino_primo_falcon1.html`, con asset in `documenti per sito/assets_fondazione/`.

## File principali

- `index.html`: homepage generale.
- `css/style.css`: stile condiviso.
- `sezioni/`: pagine HTML autonome, incluse SpaceX, Storia SpaceX, lanci imminenti, storico lanci, Starship e pad di lancio.
- `pad_di_lancio/`: infografiche e fonti usate dalla pagina dei pad.
- `03_script/genera_sito_rivoluzione.py`: generatore locale che ricostruisce il sito dai dati del progetto.
