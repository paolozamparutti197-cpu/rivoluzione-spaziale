# Flight 15: rimando nel cruscotto SpaceX

Verifica editoriale: 13 ottobre 2026.

## Modifica richiesta

Il cruscotto della sezione SpaceX presenta per primo il dossier `documenti per sito/spacex_starship_flight15_preparazione.html`. Conservati i rimandi allo sviluppo e al resoconto Flight 14; conservati i KPI 715 / 99.3% / 670. Non sono stati modificati workbook, registro operativo o notizia breaking (Ship 40).

La pagina Sviluppo Starship aggiunge una sezione di prospettiva editoriale distinta dai voli completati. La data generale della cronologia da Excel non è stata alterata.

## Ricerca e limiti

- Intervento Musk del 10 ottobre: trascrizione/registrazione su Elon Musk Archive, confronto TeslaNorth e Teslarati. Post X originale non accessibile direttamente (403).
- SpaceX: risultati Flight 14 e aggiornamento sulle operazioni orbitali, letti anche dalle versioni indicizzate perché la pagina dinamica non esponeva testo al lettore web.
- Next Spaceflight (gruppo NSF): schede B22/S42, date delle prove criogeniche e associazione attesa al volo. Non equiparate a un manifesto SpaceX definitivo.
- Reportage NSF del 9 ottobre: URL individuato, testo integrale non accessibile (403); nessun dettaglio tecnico ricavato soltanto dal titolo.
- FAA: pagina ambientale Starbase e Final Tiered EA sul ritorno al sito. Distinzione esplicita tra valutazione ambientale e modifica della licenza; nessuna autorizzazione specifica Flight 15 verificata nelle pagine consultate.
- Calendari confrontati: precedente NET 19 ottobre; NET 8 novembre in resoconti di pianificazione; nessuno adottato come giorno ufficiale. 7-21 novembre è soltanto il calcolo delle 4-6 settimane dal 10 ottobre.
- Nessun T-0, carico definitivo, numero di orbite o evento live dedicato presentato come confermato. Nessun countdown artificiale.
- Foto preesistente Ship 39 in pubblico dominio; didascalia distingue espressamente lo scafo da Ship 42.

## Manutenzione

`03_script/genera_sito_rivoluzione.py` contiene il rimando persistente, `flight15_preview()` e `flight15_pending()`. Quest’ultima gestisce metriche numeriche memorizzate come stringhe e toglie la previsione dal cruscotto e dalla sezione dedicata dopo la registrazione del quindicesimo volo. In presenza di dati numerici non interpretabili non dichiara un volo futuro.

Il dossier resta consultabile come quadro datato. I suoi link permanenti non dipendono dall’esistenza futura dell’ancora della preview. `PUBLISH_FILES` dell’aggiornatore lanci include il nuovo HTML. Ricerca full-text rigenerata con `navigazione_spacex.py`; nessun processo periodico aggiunto.

Per aggiornare le notizie cambiare il testo del dossier e le brevi anticipazioni nel generatore, poi rigenerare le sole pagine interessate e la ricerca. Non dedurre automaticamente una data certa da un calendario NET.

## Controlli

- Generazione mirata SpaceX/Starship dai dati locali, senza riscrivere Excel.
- Regressione: metrica voli `15` sia numerica sia stringa, oppure volo operativo 15, disattiva la previsione; casi verificati senza scrittura dei registri.
- `navigazione_spacex.py --check`: nessuna modifica pendente.
- Browser locale 1440 e 390 px: rimando, KPI, fotografie, link interni, tabella mobile scorrevole e ricerca del nuovo dossier. Lettura verificata anche senza JavaScript.
- Script e schermate di QA in `99_temporanei/flight15`, esclusi da Git. Il controllo può essere eseguito online con `FLIGHT15_ONLINE=1`.

La prosa segue lo stile Paolo: italiano analitico e naturale, senza enfasi artificiale; annunci, osservazioni e interpretazione restano distinti.
