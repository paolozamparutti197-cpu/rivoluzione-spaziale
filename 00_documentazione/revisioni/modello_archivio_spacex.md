# Archivio SpaceX: modello e aggiornamento

Edizione iniziale: 10 ottobre 2026. Gli Excel, i registri e i Python esistenti restano le fonti originali e non vengono modificati.

## Unità e relazioni

- **Missione**: un obiettivo identificato. Un identificatore del registro principale oppure, per le prove integrate non presenti nell'Excel lanci, `IFT-xx`.
- **Tentativo**: una finestra di lancio documentata, con stato decollato, annullato o ignoto. Le fonti attuali documentano i decolli, non tutte le finestre annullate. Un record decollato non prova che fosse il primo tentativo.
- **Lancio**: un decollo, collegato a missione e tentativo. Non comprende static fire, prove a terra o finestre annullate. Il registro delle prove qui integrato comprende i voli integrati Starship, non tutti i salti dei prototipi.
- **Esito del carico**: risultato del dispiegamento documentato separatamente dal generico esito missione. Il successo del lancio non riempie un esito payload mancante. Il numero di payload non equivale al numero di satelliti entrati in servizio.
- **Booster / veicolo**: un esemplare fisico con identificativo attestato. Una posizione senza matricola resta senza matricola, non diventa un nuovo veicolo noto.
- **Volo del booster / veicolo**: partecipazione di un esemplare o di una posizione non identificata al lancio; numero progressivo solo se documentato. Falcon Heavy ha tre posizioni (centrale, laterale A e B). A e B sono ordine di registro, non lato destro/sinistro.
- **Tentativo di recupero**: tentativo di riportare un veicolo in condizioni di recuperabilità. Il ritorno sperimentale in mare è distinto dal recupero fisico. EXP e N/A indicano assenza di tentativo nel registro. Le celle vuote indicano informazione mancante.
- **Recupero riuscito**: l'atterraggio/cattura riuscito attestato dal registro, distinto dal successivo recupero fisico in mare e dalla sopravvivenza nel trasporto. Un ammaraggio controllato da solo non è un recupero fisico riuscito.

## Perimetri

Il valore predefinito mostra le missioni Falcon dell'archivio principale. Tutti i voli integrati Starship sono consultabili nel perimetro sperimentale. Il volo 14 è una sola missione, con due classificazioni conservate: fase Operativo nell'Excel e presenza nel registro di sviluppo. Rimane nel gruppo «orbita con carico (fase mista)», selezionabile esplicitamente, senza attribuirgli una maturità operativa dimostrata. Orbita, carico e fase del programma sono campi separati. Le prove precedenti restano prove anche quando trasportano carichi di verifica.

## Fonti e riconciliazione

Lanci e booster Falcon: foglio elenco di lanci_spacex.xlsx. Rientri del volo 14: recuperi_veicoli dello stesso file. Prove integrate: «Voli integrati» di sviluppo_starship.xlsx e monografie/starship/voli.json. Matricole delle prove sono estratte dal campo Veicolo dell'Excel sviluppo; il suffisso -2 indica reflight e non un nuovo booster. Non si assegnano progressivi ai primi voli per deduzione.

Il sito storico espone riepiloghi: confronto dei totali e dell'ultima missione, senza rivendicare una verifica riga per riga di una tabella non pubblicata. Le divergenze fra registri Starship restano riportate nelle schede con entrambi i testi. Le somme dei flag Excel sono una statistica del registro, non una verifica indipendente degli eventi. Le fonti web già associate sono riportate come riferimenti: un URL non costituisce prova che il suo contenuto sia stato verificato durante questo aggiornamento.

Ogni importazione conserva hash SHA-256, foglio e riga. I dati mancanti restano null. Le normalizzazioni e le divergenze sono in registro-correzioni.json; nessuna riscrive gli originali. I riepiloghi usano il medesimo aggregatore della ricerca e gli stessi filtri. Recuperi e riuso si contano per volo di veicolo, lanci per identificativo di lancio distinto. I veicoli distinti si contano solo sulle matricole presenti; non indicano la consistenza della flotta attiva.

## Compatibilità e manutenzione

La nuova sezione archivio/spacex è statica e autonoma. Nessuna dipendenza viene aggiunta ai Python di gestione; la rigenerazione abituale non cancella questa directory. L'ingresso è nel collegamento persistente di sezioni/monografie-spacex.html. L'atlante resta invariato.

Per aggiornare la fotografia dei dati, eseguire `03_script/aggiorna_archivio_spacex.ps1`. Legge gli XLSX in sola lettura, importa anche il registro JSON e confronta il sito corrente, poi esegue il costruttore Node. Se il sito storico è più vecchio, la discrepanza viene documentata senza scartare i dati Excel. Il confronto Excel/sito va quindi eseguito dopo il normale aggiornamento del sito. L'archivio espone sempre la data dell'importazione e l'ultima data presente; non finge di aggiornarsi automaticamente. Le modifiche future allo schema o nuove sigle non riconosciute vengono bloccate oppure segnalate, senza diventare zero.

Validazione: unicità dei lanci; relazioni fra record; tre posizioni Falcon Heavy; nessun doppio volo 14; flag ammessi; date e numeri coerenti; successo recupero senza tentativo; matricole duplicate nello stesso lancio. Le incoerenze già esistenti sui progressivi sono segnalate come anomalie delle fonti e non corrette automaticamente.
