# Rivoluzione Spaziale

Sito statico multipagina del progetto "Rivoluzione Spaziale".

La home presenta il tema generale della rivoluzione spaziale in atto e collega solo le sezioni principali di primo livello. La sezione SpaceX e gia attiva; le altre pagine sono predisposte come sezioni autonome in costruzione.

Regola di architettura: la navigazione globale e la homepage non devono elencare sottosezioni operative. Lanci imminenti, storico lanci, Starship e Pad di lancio sono pagine interne alla sezione SpaceX. In futuro potranno esistere sottosezioni equivalenti per altre compagnie, ma non vanno messe nella nav principale.

Tra i dossier SpaceX attivi sono disponibili l'agenda lanci, lo storico Falcon, Starship e la pagina "Pad di lancio", con mappa interattiva e schede ricavate dalle infografiche locali. Questi link devono restare dentro `sezioni/spacex.html`.

## File principali

- `index.html`: homepage generale.
- `css/style.css`: stile condiviso.
- `sezioni/`: pagine HTML autonome, incluse SpaceX, lanci imminenti, storico lanci, Starship e pad di lancio.
- `pad_di_lancio/`: infografiche e fonti usate dalla pagina dei pad.
- `03_script/genera_sito_rivoluzione.py`: generatore locale che ricostruisce il sito dai dati del progetto.
