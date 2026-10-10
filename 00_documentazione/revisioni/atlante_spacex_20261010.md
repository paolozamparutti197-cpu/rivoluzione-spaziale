# Secondo upgrade: atlante tecnico SpaceX

Edizione e verifica: 10 ottobre 2026.

## Risultato

Sezione autonoma in atlante/spacex: 32 schede, catalogo con ricerca e filtri, confronto fra tre lanciatori, pagina di metodo e crediti. 34 immagini documentate, distribuite in 64 figure nelle schede, e 32 schemi SVG originali. Le figure comprendono fotografie e visualizzazioni scientifiche, identificate nelle didascalie.

Famiglie: Veicoli 8; Motori 5; Sistemi 3; Programmi 3; Reti 5; Infrastrutture 6; Operazioni 2.

L’inventario precedente comprendeva cinque monografie con 104 capitoli, oltre alla storia generale e ai dossier. Mancavano schede tecniche trasversali autonome: l’atlante aggiunge questo livello di consultazione senza riscrivere i libri.

## Contenuti

- Falcon 1 (Storico): atlante/spacex/falcon-1.html
- Falcon 9 (Operativo): atlante/spacex/falcon-9.html
- Falcon Heavy (Operativo): atlante/spacex/falcon-heavy.html
- Merlin (Operativo): atlante/spacex/merlin.html
- Kestrel (Storico): atlante/spacex/kestrel.html
- Dragon cargo: prima generazione (Storico): atlante/spacex/dragon-cargo-1.html
- Crew Dragon (Operativo): atlante/spacex/crew-dragon.html
- Cargo Dragon 2 (Operativo): atlante/spacex/cargo-dragon-2.html
- Draco (Operativo): atlante/spacex/draco.html
- SuperDraco (Operativo): atlante/spacex/superdraco.html
- Super Heavy (Sperimentale): atlante/spacex/super-heavy.html
- Ship (Sperimentale): atlante/spacex/ship.html
- Raptor (In sviluppo): atlante/spacex/raptor.html
- Scudo termico di Ship (In sviluppo): atlante/spacex/scudo-starship.html
- Hot staging (Sperimentale): atlante/spacex/hot-staging.html
- Rifornimento orbitale (In sviluppo): atlante/spacex/rifornimento-orbitale.html
- Starship HLS (In sviluppo): atlante/spacex/hls.html
- Starlink: generazioni dei satelliti (Operativo): atlante/spacex/starlink-generazioni.html
- Collegamenti laser Starlink (Operativo): atlante/spacex/starlink-laser.html
- Terminali Starlink (Operativo): atlante/spacex/starlink-terminali.html
- Direct to Cell (Operativo): atlante/spacex/direct-to-cell.html
- Starmind e AI1 (In sviluppo): atlante/spacex/starmind.html
- Starbase (Operativo): atlante/spacex/starbase.html
- Cape Canaveral e Kennedy (Operativo): atlante/spacex/cape-canaveral.html
- Vandenberg (Operativo): atlante/spacex/vandenberg.html
- McGregor (Operativo): atlante/spacex/mcgregor.html
- Hawthorne (Operativo): atlante/spacex/hawthorne.html
- Redmond e produzione Starlink (Operativo): atlante/spacex/redmond.html
- Recupero dei booster Falcon (Operativo): atlante/spacex/recupero-falcon.html
- Recupero del sistema Starship (Sperimentale): atlante/spacex/recupero-starship.html
- Stazioni a terra Starlink (Operativo): atlante/spacex/stazioni-terra.html
- Red Dragon (Abbandonato): atlante/spacex/red-dragon.html

## Collegamenti

Rimandi reciproci in 46 capitoli sorgente dei libri, cinque indici e 10 pagine storiche/manuali. Accesso principale nella pagina persistente sezioni/monografie-spacex.html. Ogni scheda ha collegamenti a schede vicine e capitoli di approfondimento; i registri delle missioni restano nei libri.

## Persistenza

I 28 Python esistenti sono identici al baseline SHA-256 preso prima del lavoro. Nessuna modifica ai batch di manutenzione, ai workbook o al generatore generale. Le pagine statiche dell’atlante restano nel repository; le normali rigenerazioni non le eliminano. I rimandi nei libri sono salvati nei contenuti sorgente e sono stati confermati dalla rigenerazione di tutti e cinque i libri.

La fonte delle nuove schede è atlante/spacex/schede.json. build.mjs è un generatore Node facoltativo, indipendente, senza pacchetti esterni; scrive soltanto nella propria cartella. La pubblicazione ordinaria usa i file già generati e non dipende da questo comando.

## Fonti e limiti

44 riferimenti nel catalogo: documenti SpaceX, NASA, FAA, FCC, operatori e relazioni tecniche. I riferimenti ripresi dalle monografie mantengono le note di data e provenienza. Verifiche aggiuntive sulla guida Falcon v8, materiali NASA Dragon/CRS, relazione Falcon 1 e specifiche Standard Starlink.

Separati: configurazioni storiche e attuali; dichiarazioni del costruttore e prove; recupero e rivolo; autorizzazioni e flotta attiva; trasferimento interno di propellente e trasferimento fra due navi. Le schede non inventano spinte, ritmi di produzione o capacità quando manca un riferimento adeguato. La guida Falcon v8 riporta totali di spinta non uniformi: il dato Merlin individuale è attribuito al testo della guida e la discrepanza è dichiarata.

Riuso completo Starship, rifornimento fra veicoli, qualifica HLS, servizio V3 esteso e sostenibilità Starmind rimangono questioni aperte. Questo upgrade non certifica tutte le affermazioni presenti nel resto del sito e non modifica il dossier finanziario Q2 preesistente.

Le foto vengono dai materiali già accreditati, più una fotografia NASA Cargo Dragon del 27 novembre 2022. La pagina metodo.html raccoglie fonti, autori e condizioni. Le immagini di altri programmi sono dichiarate di contesto. Gli SVG sono schemi funzionali non in scala, non copie delle tavole proprietarie.

## Verifica locale

- 96 pagine pubbliche coinvolte: 2.970 riferimenti locali controllati; nessun file o frammento mancante, nessun ID duplicato.
- 226 controlli iniziali e 102 controlli finali di pagina a 1.440, 390 e 360 px: nessuna immagine mancante, nessuno scorrimento orizzontale indesiderato, nessun errore JavaScript.
- Ricerca Raptor, filtro Motori (5), filtro Motori + Storico (1), nessun risultato e azzeramento (32) verificati.
- Schemi scorribili su telefono a una dimensione leggibile, con accesso al file completo. Tutti i 32 SVG verificati per testo entro la tavola; controllo visivo di catalogo e schede rappresentative.
- Baseline e risultati conservati in 99_temporanei/atlante110, cartella ignorata da Git.

## Pubblicazione

Destinazione: GitHub Pages, ramo gh-pages dello stesso repository. Verificare il workflow sul commit nuovo e confrontare i file pubblici prima di considerare terminata la consegna.
