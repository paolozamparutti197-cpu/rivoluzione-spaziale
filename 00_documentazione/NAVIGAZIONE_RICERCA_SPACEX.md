# Navigazione e ricerca SpaceX

Edizione 11 ottobre 2026. Implementazione del quarto prompt di `per110.md`.

## Ingressi pubblici

- `sezioni/percorsi-spacex.html`: capire SpaceX, consultare dati, seguire missioni, approfondire programmi; itinerari trasversali per principianti ed esperti.
- `sezioni/cerca-spacex.html`: ricerca nel testo con estratti, filtri per tipo e argomento, risultati paginati e URL condivisibile.
- Le pagine della sezione, i capitoli, i dossier collegati e le schede dell’archivio hanno breadcrumb, ricerca rapida e accesso ai percorsi.

I cinque libri attualmente presenti sono Crew Dragon, Starlink, Starship, Artemis e Starmind. Gli argomenti derivano dal testo, non dal titolo soltanto; i filtri non indicano uno stato operativo del programma.

## Fonte e aggiornamento

`03_script/navigazione_spacex.py` è la sola fonte di pagine guida, breadcrumb e indice. Usa esclusivamente la libreria standard Python. Legge gli HTML pubblici; non legge né scrive Excel, non consulta servizi esterni e non modifica i testi degli articoli.

```powershell
python -X utf8 03_script/navigazione_spacex.py
python -X utf8 03_script/navigazione_spacex.py --check
```

Il primo comando è idempotente: esecuzioni successive senza nuovi contenuti non cambiano i file. Il secondo controlla che guide, decorazioni e indice siano aggiornati, senza salvarli. Dopo correzioni manuali o nuovi articoli eseguire il primo, prima di pubblicare.

L’indice `ricerca/spacex.json` conserva titolo, percorso, categoria, argomenti e testo. Non indicizza cartelle `outputs`, `tmp`, backup o i testi sorgente `contenuti`, evitando copie dello stesso capitolo. Gli articoli sono individuati seguendo i collegamenti delle pagine SpaceX. Una pagina nuova non collegata non diventa automaticamente un risultato. Il documento locale `spacex_q2_2026_earnings.html`, già modificato prima di questo lavoro, è lasciato intatto ed escluso dall’indice per non pubblicare materiale di lavoro non pertinente.

I blocchi HTML `LETTORI:HEAD` e `LETTORI:NAV` sono gestiti dallo script. Non modificarli manualmente: cambiare il generatore. CSS isolato in `css/lettori-spacex.css`, JavaScript in `js/lettori-spacex.js`, senza regole globali che mescolino tema chiaro e scuro.

## Integrazione dei generatori

I cinque `genera_monografia_*.py` eseguono l’aggiornamento di ricerca e navigazione dopo aver scritto i libri. Anche `costruisci_archivio_spacex.mjs` lo esegue dopo schede e riepilogo; usa `python` oppure l’eseguibile indicato da `SPACEX_PYTHON`.

Il generatore generale `genera_sito_rivoluzione.py` conserva il nuovo riepilogo storico se l’archivio esiste. Dopo la generazione aggiorna l’archivio mediante il nuovo ingresso `aggiorna_archivio_spacex.py`, equivalente all’importatore PowerShell ma indipendente dalla sua execution policy. Importa i workbook in sola lettura, conserva le impronte delle fonti e verifica che Excel non sia cambiato. Usa Python/openpyxl e Node, già presenti nel progetto, poi ricostruisce la navigazione. Lo script PowerShell esistente resta disponibile. Se l’importazione fallisce, l’errore interrompe la procedura: non pubblicare come completo un aggiornamento parziale.

`aggiorna_lanci_spacex_sito.py` include nella propria lista di pubblicazione anche indice, guide, risorse della ricerca e archivio, evitando che l’agenda venga pubblicata senza i risultati aggiornati. Non è stata introdotta un’automazione ricorrente.

## Ricerca, accessibilità e prestazioni

- L’indice è richiesto soltanto nella pagina ricerca. Le altre pagine caricano un piccolo script che termina immediatamente: nessun download full-text durante la lettura.
- Ricerca senza distinzione fra maiuscole/minuscole o accenti; parole comuni delle domande italiane ignorate; tutte le parole significative devono comparire. È una ricerca lessicale, non un sistema semantico AI.
- Titoli pesano più delle occorrenze nel testo; estratti mostrano il contesto. Ogni risultato è un normale collegamento, non un contenuto caricato dinamicamente nel libro.
- Venti risultati iniziali, pulsante per i successivi; filtri combinabili, stato annunciato ai lettori di schermo, etichette esplicite, pulsanti e link raggiungibili da tastiera.
- Senza JavaScript restano utilizzabili i percorsi, gli indici dei libri e gli elenchi statici dell’archivio. In caso di errore del download viene indicata un’alternativa.
- Nessun tracking, servizio esterno di ricerca, animazione decorativa o libreria aggiuntiva.

## Verifiche e pubblicazione

Helper di test in `99_temporanei/verifica_lettori.py` e `verifica_lettori.cjs`: link, idempotenza, rigenerazione dei cinque libri su copia isolata e conservazione dello storico; ricerca, filtri, invio da tastiera e layout 1440/390 pixel. I test non modificano i workbook originali.

Pubblicare i percorsi pertinenti soltanto, non `git add .`. Dopo il commit: `git push origin main`, poi `git push origin main:gh-pages`, attendere Pages e verificare HTML, CSS, JS e indice realmente online. Conservare i file preesistenti non pertinenti e consultare la nota `NOTE_GITHUB_PAGES_MAIN_VS_GHPAGES.txt`.
