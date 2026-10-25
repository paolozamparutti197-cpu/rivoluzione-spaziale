# Merlin: integrazioni documentali del 25 ottobre 2026

Riferimento prima dell’intervento: `03465767b81b5e08a7942aefd0678ae2ab20f425`.
Pagina: `atlante/spacex/merlin.html`.

## Contenuti aggiunti

- Riquadro iniziale «In breve».
- Tabella di 13 parametri per M1D e MVac, subito dopo la configurazione di riferimento: condizioni, unità, fonti e dati non dichiarati.
- Tabella di nove configurazioni storiche e operative, dopo il capitolo delle origini: 1A, 1B, 1C, tre riferimenti 1D e tre MVac.
- Note sul modello pubblico Sierra del 2019: pressione alla faccia dell’iniettore, espansione, miscela del generatore e ambiguità del rapporto O/F.
- Provenienza dei 30.000/36.000 giri/min, con limiti del confronto.
- Attuatori idraulici, fuel trim, controllo del lanciatore e confronto fra campi di regolazione delle guide 2015 e 2025.
- Materiali e raffreddamento del MVac storico, rapporti di espansione, limiti documentali dell’estensione corta e anomalia del luglio 2024.
- Cronologia CRS-1, marzo 2020, febbraio 2021 e luglio 2024, distinguendo guasto iniziale, controllo del motore, missione e recupero.
- Traguardi datati di riuso del booster e del singolo motore; manutenzione e dati di vita non pubblicati.
- Merlin 2, confronto con Raptor e collegamenti interni verificati.
- Glossario di sei termini.
- Fotografia originale SpaceX del Merlin 1D a McGregor, circa 2012, con licenza CC0, permessi VRT e SHA-1 controllati. La fotografia si aggiunge alle quattro ricostruzioni.
- Indice esteso da 13 a 23 collegamenti e 21 nuovi riferimenti aggiunti dopo i 14 originari.

## Correzioni e precisazioni

Nessun paragrafo dei tredici capitoli originali è stato corretto, accorciato o parafrasato. Il solo campo «Stato» è stato precisato per distinguere le versioni operative, quelle storiche e 1B non volato.

Le integrazioni correggono possibili letture improprie dei dati, senza sostituire quelli già presenti:

- Le guide SpaceX del 2015 e del 2025 descrivono configurazioni diverse. Il minimo MVac del 2015, 81.000/210.000 lbf (circa 38,6%), non viene combinato con il massimo 2025. Nel 2025 140.679/220.500 corrisponde a circa 63,8%.
- La pressione nominale del rapporto Sierra del 2019 è una pressione di ristagno alla faccia dell’iniettore, non una misura pubblica della pressione statica dell’attuale camera. L’ambiguità interna O/F 2,356 / 2,58 rimane esplicita.
- NASA 2021 e l’intervista Musk 2018 non identificano condizioni sufficienti per trattare 30.000 e 36.000 giri/min come specifiche contraddittorie.
- La tripla architettura descritta nella guida Falcon appartiene all’avionica del lanciatore; non viene automaticamente assegnata a ciascun controller motore.
- L’alcol isopropilico del marzo 2020 è distinto dalla vernice dei generatori nell’autunno 2020. La fonte di Musk è collegata direttamente al messaggio originale; NASA ASAP conserva lo stato di causa probabile ancora in verifica nel maggio 2020.
- Per febbraio 2021 non viene inventato il momento preciso dello spegnimento a partire dalla sola conseguenza sul recupero.
- Nel luglio 2024 il carico comprendeva 20 satelliti, secondo SpaceX. L’aggiornamento investigativo parla della causa più probabile: non è presentato come chiusura formale dell’indagine FAA.
- Il successo primario CRS-1 è distinto dalla perdita del prototipo ORBCOMM, documentata dai comunicati della società depositati presso SEC.

Per ogni nuovo nucleo, il file `merlin_integrazioni_verifica_20261025.json` registra fonte originale, versione/condizioni e confronto o verifica interna. Non vengono inventate conferme indipendenti: più pubblicazioni SpaceX o una ripresa FAA della stessa prova restano attribuite alla medesima origine.

## Dati che restano aperti

Masse e rapporto spinta/peso attuali, Isp attuali nella guida 2025, spinta nel vuoto del singolo M1D, pressione statica e O/F attuali, caratteristiche complete dell’estensione MVac corta e materiali di ogni revisione, architettura interna dei controller attuali, regime nominale/massimo e modifiche della turbopompa, limiti del fuel trim, record assoluti aggiornati di ogni esemplare, accensioni e tempi cumulativi, intervalli di manutenzione e sostituzioni.

I 37 voli del booster sono un traguardo SpaceX del 25 agosto 2026; le 22 missioni del singolo Merlin un traguardo del 23 febbraio 2024. Non sono trattati come record contemporanei o come storia dello stesso hardware.

## Conteggio e incremento informativo

| Criterio | Prima | Dopo |
|---|---:|---:|
| Testo del contenuto principale, con bibliografia | 4.029 | 8.426 |
| Senza bibliografia | 3.581 | 6.916 |
| Dentro l’articolo dei capitoli, comprese le nuove sottosezioni | 2.651 | 5.150 |

Il conteggio usa il medesimo parser della revisione precedente: titoli, testo, dati, didascalie, titoli accessibili delle tabelle e fonti nel `main`; esclusi navigazione, comandi e numeri dei rimandi bibliografici. Apostrofi e trattini interni mantengono una parola. La soglia di 3.000 è superata anche escludendo l’intera bibliografia.

L’inventario precedente comprendeva 54 nuclei (30 iniziali e 24 aggiunti nella revisione precedente). Questo intervento ne registra altri 24: incremento del **44,4%**. Non vengono contati come aggiunte la disposizione in tabella di fatti già presenti, le ripetizioni, il glossario e gli elenchi di dati non verificati. È una misura editoriale riferita a quell’inventario, non un indice universale della quantità di informazione.

## Conservazione e verifiche

- Confronto DOM con `0346576`: tutti i titoli e paragrafi dei 13 capitoli, didascalie originali, galleria, fotografie precedenti, navigazione, footer e primi 14 riferimenti conservati.
- Dati dei capitoli e `schede.json` identici dopo normalizzazione CRLF/LF. Nessuna modifica agli asset originali, ai CSS precedenti o ai JavaScript.
- JPEG e WebP precedenti identici byte per byte; SVG e sorgenti testuali uguali al riferimento Git normalizzando le sole terminazioni di riga del checkout Windows.
- Solo `merlin.html` modificata fra le pagine HTML del sito. Nessun’altra scheda, schema o monografia modificati dalla rigenerazione.
- Nu HTML Checker W3C: **nessun messaggio, nessun errore** sul documento finale.
- ID univoci, ancore e file dei collegamenti locali verificati; tabelle con caption, intestazioni `scope`, regione scorribile selezionabile e note leggibili fuori dall’area di scorrimento.
- Chromium a 1440, 768, 390 e 320 pixel, con e senza JavaScript: nessun allargamento della pagina, immagini decodificate, nessun errore JavaScript o richiesta locale fallita.
- Avvio/arresto GIF, poster per movimento ridotto e zoom verificati. Tabelle scorribili anche da tastiera.
- Verifica via HTTP locale a 1440 e 390 pixel: tutti i quattro CSS caricati e analizzati; valori numerici allineati a destra; fotografia 921 × 614; nessun overflow.
- Controllo visivo di tabelle, glossario, fotografia e riquadro iniziale. Le quattro vedute conservano resa e didascalie.
- Conversioni lbf/N, psi/Pa e percentuali controllate con NIST e calcoli automatici. Nessuna formula originaria modificata.
- `git diff --check` superato. Nessuna dipendenza aggiunta o aggiornata.

Test ripetibili: `prototipi/merlin-vedute/verifica_editoriale.py`, `verifica_pagina.cjs` e `verifica_integrazioni.cjs`. Le schermate locali e i risultati browser sono nella cartella QA ignorata dal repository.

## Rilascio

Commit dedicato, seguito da push atomico verso `main` e `gh-pages`, senza force push. L’accesso GitHub è stato verificato con permesso di push attivo. La verifica di rilascio confronta il documento pubblico con il file locale e controlla l’esito del build GitHub Pages; hash del commit ed esito effettivo vengono riportati nel messaggio conclusivo.
