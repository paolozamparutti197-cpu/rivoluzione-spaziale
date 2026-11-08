# Countdown Flight 15 nel cruscotto SpaceX

Richiesta dell’8 novembre 2026: inserire giorni, ore, minuti e secondi nello spazio sotto le schede Stato Starship, indicato con una X nello screenshot.

## Orario e significato

L’articolo breaking effettivamente online è `spacex_starship_flight15_ufficiale.html`, non il precedente dossier del 6 novembre. Il progetto locale era tre commit indietro: allineato prima della modifica, conservando le modifiche non pubblicate, compreso il breadcrumb del vecchio articolo.

- Apertura: 13 novembre 2026, 22:45 UTC = 23:45 CET in Italia = 16:45 CST in Texas.
- Durata: 75 minuti.
- Fine: 14 novembre 2026, 00:00 UTC = 01:00 CET.
- Data obiettivo, autorizzazioni ancora necessarie: il timer non promette un decollo all’apertura.

Fonti consultate: breaking news corrente e sua fonte primaria [SpaceX, pagina Flight 15](https://www.spacex.com/launches/starship-flight-15); riscontro nel [servizio KRGV del 7 novembre](https://www.krgv.com/news/spacex-sets-target-date-for-15th-starship-launch-at-starbase/), che riporta il comunicato e l’apertura alle 16:45 locali, e nel [registro Orbit Codex](https://orbitcodex.com/operations/flight-15-starship), che riporta 22:45–00:00 UTC. La pagina dinamica SpaceX restituisce soltanto il titolo al lettore testuale: non è stata presentata come testo integralmente accessibile.

## Implementazione e manutenzione

Unica configurazione `FLIGHT15_WINDOW` in `03_script/genera_sito_rivoluzione.py`: inizio/fine ISO UTC, dossier aggiornato, fonte e data della verifica. `flight15_window_countdown()` crea la scheda persistente sotto `status-stack`. Il link Flight 15 non mostra più la stima di ottobre ma la breaking aggiornata e l’orario attuale.

CSS e JavaScript isolati in `css/countdown-finestra.css` e `js/countdown-finestra.js`, inclusi nel manifest di pubblicazione. I contatori preesistenti dell’agenda non sono stati cambiati. Il nuovo timer usa istanti assoluti, cifre tabulari senza animazioni e non annuncia ogni secondo agli screen reader. Aggiorna la differenza dall’orologio del dispositivo, non decrementa un contatore soggetto a deriva.

Stati: attesa, finestra prevista in corso, finestra prevista terminata, orario non disponibile. Nessun numero negativo e nessuna dichiarazione automatica di decollo. La scheda viene omessa dal generatore quando Flight 15 risulta registrato come completato. In assenza di JavaScript rimangono data, ora e avvertenza.

Per rinvii modificare gli istanti nella configurazione, aggiornare il riferimento di verifica e rigenerare la sezione. Le etichette italiane, UTC e Texas, la durata e la scheda superiore derivano dagli stessi istanti tramite `flight15_window_times()`, che gestisce anche l’ora legale e rifiuta finestre non valide. Gli orari restano un dato editoriale verificato: non viene interrogato un servizio esterno in ogni browser.

Nessuna modifica ai workbook o ai conteggi 721 / 99.3% / 676, alla breaking corrente o agli articoli. Le altre modifiche locali non sono incluse nella pubblicazione.

Controlli locali e online: cinque larghezze (1440, 1308, 768, 390, 320), tre fusi (Roma, Chicago, Tokyo), cambio del secondo, attraversamento dello zero, fine finestra, timestamp non valido, link al dossier, lettura senza JavaScript e assenza di errori/overflow. Script e screenshot in `99_temporanei/flight15/countdown-qa.cjs` e `countdown-*.png`, esclusi da Git.
