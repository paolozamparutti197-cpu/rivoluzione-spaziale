Cartella SpaceX - guida rapida per nuove sessioni
=================================================

Questa cartella contiene due workbook operativi:
- 01_workbook\lanci_spacex_falcon.xlsx: registro dei lanci SpaceX/Falcon.
- 01_workbook\sviluppo_starship.xlsx: workbook analitico sul programma Starship.

Nota git: workbook, backup, sorgenti Office, temporanei e output HTML intermedi sono dati locali di lavoro e sono ignorati da .gitignore. Gli script, gli HTML pubblici, le immagini pubblicate, le fonti e i file guida devono invece restare versionati quando cambiano.

Se una nuova sessione deve capire rapidamente il contesto, partire da qui e poi leggere:
- 00_documentazione\README_manutenzione.txt
- 00_documentazione\procedure_aggiornamento.txt
- 00_documentazione\storico_sessioni_lavoro.txt
- 00_documentazione\inventario_file.txt
- 00_documentazione\README_infografiche_pad.txt se la richiesta riguarda infografiche o pad di lancio.

Regola piu' importante
----------------------
Non modificare mai gli .xlsx a livello ZIP/XML.

Errore gia' successo: una riscrittura diretta dell'xlsx come pacchetto XML era leggibile da openpyxl, ma Excel lo segnalava come danneggiato. Per qualunque modifica reale ai workbook usare Excel COM, salvare da Excel e poi riaprire in sola lettura con Excel per verificare.

Procedura standard per aggiornare un workbook
---------------------------------------------
1. Verificare le fonti online se i dati possono essere cambiati.
2. Leggere il workbook corrente in sola lettura.
3. Creare un backup in 02_backup con timestamp.
4. Scrivere usando Excel COM.
5. Salvare da Excel.
6. Riaprire il file con Excel COM in read-only e controllare le celle modificate.
7. Chiudere eventuali processi EXCEL nascosti creati dall'automazione.
8. Aggiornare 00_documentazione\storico_sessioni_lavoro.txt se la sessione ha aggiunto informazioni utili.

Struttura cartella
------------------
- 00_documentazione: note operative, storico, prompt, audit e istruzioni di manutenzione.
- 01_workbook: file Excel correnti da usare come sorgente operativa.
- 02_backup: copie storiche da non modificare e non sovrascrivere.
- 03_script: script di supporto.
- 04_dati_geo: file geografici KML/KMZ o simili.
- 05_fonti_originali: documenti sorgente usati dagli script, se disponibili.
- pad_di_lancio: infografiche PNG sui pad di lancio SpaceX e asset fotografici riutilizzabili.
- 99_temporanei: file vuoti, lock, prove e materiale non operativo.

Sito Rivoluzione Spaziale
-------------------------
- Il sito pubblico e' statico multipagina ed e' generato da 03_script\genera_sito_rivoluzione.py.
- File pubblici principali:
  - index.html
  - css\style.css
  - sezioni\*.html
  - pad_di_lancio\*.png per la pagina Pad di lancio.
- Gerarchia editoriale:
  - la homepage e la nav globale mostrano solo il primo livello: Home, SpaceX, Blue Origin, ULA, Rocket Lab, Arianespace, Cina;
  - Luna, Marte, Infrastrutture orbitali e Cronologia restano pagine provvisorie, ma non devono apparire nella nav globale finche' non vengono ripensate come macro-sezioni vere;
  - Lanci imminenti, Storico lanci, Starship, Pad di lancio e Storia sono sottosezioni di SpaceX e devono restare collegate da sezioni\spacex.html, non da index.html o dalla nav principale;
  - sezioni\storia-spacex.html e' l'indice storico: contiene parti selezionabili. La prima parte e' "Dalla fondazione fino al primo lancio" e punta a documenti per sito\fondazione_spacex_fino_primo_falcon1.html; la seconda e' "Dal primo fallimento al quarto lancio" e punta a documenti per sito\falcon1_dal_primo_fallimento_al_quarto_lancio.html; la terza e' "Dal primo successo orbitale al contratto CRS" e punta a documenti per sito\falcon1_successo_orbitale_contratto_crs.html;
  - documenti per sito\assets_fondazione contiene le immagini usate dai dossier storici Falcon 1; la sottocartella falcon1-flight4 contiene la sequenza fotografica del quarto volo Falcon 1;
  - in futuro altre compagnie potranno avere sottosezioni equivalenti, ma sempre dentro la pagina della compagnia.
- Quando si cambia il sito, modificare il generatore e poi rigenerare gli HTML, non intervenire solo sui file HTML prodotti.
- Il sito pubblico GitHub Pages viene servito da gh-pages: dopo un commit che cambia il sito, usare git push origin main e git push origin main:gh-pages, poi verificare la URL pubblica.

Infografiche pad di lancio
--------------------------
- Aggiornate al 14/06/2026.
- Cartella: pad_di_lancio.
- Infografica originale spostata: pad_di_lancio\pad 37b.png.
- Infografiche generate: SLC-40, LC-39A, SLC-4E, SLC-6, Boca Chica Pad 1/OLP-1, Boca Chica Pad 2/OLP-2.
- Script rigenerabile: 03_script\genera_infografiche_pad.py.
- Fonti e crediti: pad_di_lancio\fonti_pad_di_lancio.md e pad_di_lancio\assets\crediti_immagini.json.
- Nota licenze: quasi tutte le foto sono pubblico dominio; OLP-1 usa foto Jenny Hautmann CC BY-SA 4.0, mantenere attribuzione.

Nomi storici
------------
- Il vecchio spacex.xlsx ora e' 01_workbook\lanci_spacex_falcon.xlsx.
- Il vecchio Sviluppp_starship.xlsx ora e' 01_workbook\sviluppo_starship.xlsx.

Stato operativo al 31/05/2026
-----------------------------
- Il workbook lanci e' aggiornato fino a:
  - nr 662, 30/05/2026, Starlink Group 17-41.
- Ultimo backup lanci creato:
  - 02_backup\lanci_spacex_falcon_backup_20260531_092528.xlsx.
- E' stato creato un audit degli errori possibili senza modificare Excel:
  - 00_documentazione\audit_errori_lanci_20260531.txt.

Note specifiche sui lanci
-------------------------
- Il foglio principale del workbook lanci e' "elenco".
- Il foglio contiene molte righe precompilate; non usare max_row per trovare l'ultimo lancio reale.
- Le righe reali hanno normalmente nr in colonna A e missione in colonna E.
- AMOS-6 e' presente nel workbook come riga numerata, ma e' un evento static-fire/pre-lancio, non un lancio completato nella lista Wikipedia.
- Quando si aggiungono lanci Falcon/SpaceX, usare come fonte primaria Wikipedia "List of Falcon 9 and Falcon Heavy launches" e, se disponibile, fonte ufficiale SpaceX o fonte giornalistica specializzata.

Note specifiche su Starship
---------------------------
- Per eventi Starship programmati o NET, aggiornare la timeline, non la tabella dei voli completati.
- Aggiornare "Voli integrati" solo quando il volo e' realmente avvenuto.
- Mantenere coerenti anche "Fonti" e "Discrepanze" quando si aggiornano eventi Starship.

File da non usare come sorgenti
-------------------------------
- Non usare file di lock Excel tipo ~$*.xlsx.
- Non usare file in 99_temporanei come sorgenti operative.
- Non modificare file in 02_backup salvo richiesta esplicita.

Per continuare in una nuova sessione
------------------------------------
Prima di lavorare, leggere questo README e poi lo storico recente. Se la richiesta riguarda aggiornamenti lanci, controllare subito l'ultima riga reale di 01_workbook\lanci_spacex_falcon.xlsx e confrontarla con le fonti aggiornate. Se la richiesta riguarda correzioni massive, produrre prima un report .txt e non modificare Excel finche' l'utente non approva.
