# Analisi originali SpaceX: quinto prompt per110

Prima edizione e revisione editoriale: 12 ottobre 2026. Tre dossier, cinque SVG originali, due modelli didattici. Dati iniziali: archivio riconciliato del 10 ottobre 2026. Dal 13 ottobre 2026 (decisione di Paolo) le analisi seguono l'archivio: a ogni ricostruzione dell'archivio serie e snapshot vengono ricalcolati sui dati correnti; la revisione editoriale del testo resta quella dichiarata.

## Sorgenti e risultati

- `contenuti/`: prosa sorgente con segnaposto espliciti per i calcoli. Non indicizzata come articoli duplicati.
- `dossier.json`: scelta motivata, finestra storica, ultima revisione editoriale e prossime scadenze.
- `fonti.json`: ruolo delle fonti, data del documento, consultazione e sezione.
- `registro-correzioni.json`: prima/dopo, motivo e prova; nuove voci aggiunte senza cancellare quelle precedenti.
- `modelli.mjs`: matematica condivisa da grafici, controlli e browser.
- `dati/calcoli.json`: numeratori, denominatori, identificatori, coppie di voli e formule.
- `dati/snapshot-archivio.json`: byte esatti del registro pubblico usato, con impronta. Gli snapshot precedenti restano nella cronologia Git, non si accumulano copie integrali a ogni aggiornamento.

## Comandi manuali

```powershell
node 03_script/genera_analisi_spacex.mjs
python -X utf8 03_script/navigazione_spacex.py
node 03_script/verifica_analisi_spacex.mjs --as-of 2026-10-12 --report
node 03_script/genera_analisi_spacex.mjs --snapshot analisi/spacex/dati/snapshot-archivio.json --check
python -X utf8 03_script/navigazione_spacex.py --check
```

Il primo comando ricalcola i dati, non aggiorna la data di revisione editoriale. Il controllo `--strict-review` restituisce un errore se una revisione è scaduta o se il registro è successivo alla revisione del testo. `--links` controlla anche i collegamenti esterni: errori 403/429 richiedono ispezione umana, non cancellazione automatica della fonte.

Le impronte dei workbook attuali sono confrontate con quelle storiche del registro e riportate. Una differenza può dipendere da dati o da metadati Excel: non dimostra da sola quali celle siano cambiate. Non invalida il calcolo sullo snapshot pubblico dichiarato, ma richiede verifica prima di chiamarlo aggiornamento all'Excel attuale. `--require-current-workbooks` rende questa differenza bloccante. Alla prima edizione l'impronta di lanci_spacex.xlsx differisce da quella dell'importazione del 10 ottobre, mentre sviluppo_starship.xlsx corrisponde. I file non vengono sovrascritti né vengono dichiarati riconciliati nuovamente.

L'aggancio in `03_script/costruisci_archivio_spacex.mjs` lavora dopo la ricostruzione dei dati e prima della ricerca. È raggiunto sia dall'ingresso Python dell'archivio sia dall'aggiornamento generale del sito. La lista di pubblicazione Python include nuove analisi e generatori, così gli aggiornamenti successivi non lasciano online grafici vecchi con dati nuovi. Nessun timer o automazione schedulata creato.

## Limiti

Falcon Heavy: un decollo e tre voli di core. Starship esclusa dalle serie Falcon. La quota dei rivoli usa tutti i voli dei booster come denominatore; ignoti dichiarati. La mediana usa soltanto coppie della stessa matricola con progressivi consecutivi e date del calendario, non ore di ricondizionamento. Il 2026 è confrontato alla stessa data del calendario, senza estrapolazioni.

Il modello dei costi usa unità convenzionali, non prezzi o costi SpaceX: `C/n + R*(n-1)/n + A`. Il modello di rinnovo usa `N/L` in regime stazionario e non simula collisioni, emissioni o rientri. Le vite del modello non sono termini legali di smaltimento. Impatto ZTF riferito al campione 2019–2021, ESA 2026 ai dati fino a fine 2025, atmosferica a studi di modellazione.

La prosa è stata rifinita seguendo stile-paolo. Foto e rendering sono riutilizzati dagli archivi già documentati, con crediti e limiti nelle pagine. Grafici originali CC BY 4.0, non licenza sulle fonti di terzi.
