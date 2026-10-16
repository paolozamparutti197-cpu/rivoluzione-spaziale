# Quinto prompt per110: contenuti originali e metodo

12 ottobre 2026. Sezione realizzata in `analisi/spacex/`; destinazione pubblica: [Analisi SpaceX](https://paolozamparutti197-cpu.github.io/rivoluzione-spaziale/analisi/spacex/index.html).

## Scelta editoriale e originalità

Tre dossier, circa 5.500 parole con fonti e didascalie, senza duplicare le monografie:

1. Cadenza e riutilizzo Falcon: serie 2017–2025, composizione Starlink/altre missioni, progressivi dei booster e intervalli fra voli. Nuovo calcolo: mediana 2025 di 38 giorni, 157 coppie della stessa matricola con progressivi consecutivi. Non viene interpretata come tempo di officina. Un modello normalizzato spiega il riuso senza inventare costi SpaceX.
2. Starship: confronto di annunci e prove, obiettivi marziani IAC 2017 conservati, primo integrato 2023, trasferimento interno 2024 e calendario HLS 2026 distinti. Risultato sperimentale, qualifica completa e scadenza mancata non sono equivalenti.
3. Megacostellazioni: bilancio stock/flussi e rinnovo N/L, servizi e alternative, astronomia, ambiente orbitale e rientri. ZTF 2019–2021 non trasformato in percentuale dell'astronomia mondiale nel 2026; ESA 2026 riferito ai dati 2025; studi atmosferici presentati come modelli, non danni globali già attribuiti a un operatore.

Cinque SVG originali, due calcolatori con formule condivise fra browser e generatore, tre figure fotografiche/rendering già documentate nel sito. Crediti e contesto dichiarati. Prosa rifinita con stile-paolo.

## Base dati e avvertenza

Calcoli sulla copia esatta dell'archivio pubblico del 10 ottobre 2026; non è un aggiornamento dei voli al 12 ottobre. Gli identificatori delle missioni e delle coppie, numeratori, denominatori, formule e impronte sono in `dati/calcoli.json`. Snapshot del registro in `dati/snapshot-archivio.json`; edizioni precedenti recuperabili dalla cronologia Git.

L'impronta di `01_workbook/lanci_spacex.xlsx` attuale differisce da quella registrata il 10 ottobre. Quella di sviluppo_starship.xlsx coincide. Non si deduce da un'impronta quali celle o metadati siano cambiati. Il workbook non è stato aperto per modifica, salvato o sovrascritto. L'avvertenza è nel rapporto locale e nelle istruzioni; `--require-current-workbooks` rende bloccante questa differenza per un aggiornamento dichiarato all'Excel attuale. Il calcolo storico sullo snapshot resta riproducibile.

## Manutenzione e controlli

- Metadati con data del documento, consultazione, revisione editoriale e prossima scadenza; non si ringiovanisce la revisione dopo un ricalcolo.
- Registro pubblico prima/dopo con due correzioni reali preesistenti, Falcon Heavy e Merlin, collegate ai relativi commit; prima edizione distinta da correzione.
- Nessuna automazione, timer o job schedulato attivato. Il normale build Pages già esistente è il solo meccanismo di pubblicazione.
- Aggancio al costruttore dell'archivio, raggiunto dagli ingressi Python esistenti, prima della rigenerazione della ricerca. Lista di pubblicazione Python estesa ai dossier e ai nuovi strumenti.
- Ricerca interna: sei pagine nuove indicizzate, sorgenti dei testi escluse dai duplicati; breadcrumb e ingresso dalla sezione SpaceX conservati nel generatore generale.
- Controlli su perimetri, tre core Heavy, snapshot, formule, mediane, progressivi ignoti, collegamenti e scadenze. Newline LF espliciti per impronte portabili, senza regole globali sui file non pertinenti.

Verifiche locali: 188 collegamenti locali, 13 ancore; 12 combinazioni pagina/viewport (1440 e 390), tre dossier senza JavaScript, cinque SVG entro i limiti. Calcolatori provati con parametri iniziali, variazioni, zero denominatore e input non validi; ripristino, focus da tastiera, scorrimento interno e contrasto delle tabelle verificati. Ricerca con una domanda reale sul ricondizionamento. Nessuna modifica agli asset Raptor o Merlin.

Comandi e limiti completi in `analisi/spacex/README.md` e nel metodo pubblico. Screenshot, rapporto browser e rapporto dei dati in `99_temporanei/analisi110/` e `99_temporanei/verifica_analisi_spacex.json`, esclusi dalla pubblicazione. Pubblicare con staging mirato e verificare Pages prima di dichiarare completato il rilascio.

## Aggiornamento 13 ottobre 2026

Decisione di Paolo: le analisi seguono l'archivio. Snapshot e calcoli vengono rigenerati con l'archivio corrente; `verifica_archivio_spacex.mjs` controlla che il taglio del confronto annuale coincida con la data dell'archivio, non piu con il 10 ottobre.
