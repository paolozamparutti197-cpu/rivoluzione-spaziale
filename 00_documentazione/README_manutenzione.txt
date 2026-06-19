README manutenzione
===================

Scopo
-----
Questa cartella e' organizzata per separare file operativi, backup, script, fonti e appunti. L'obiettivo e' evitare ambiguita' sui file da aggiornare e proteggere i workbook Excel da modifiche rischiose.

File correnti
-------------
- 01_workbook\sviluppo_starship.xlsx: workbook corrente sullo sviluppo Starship.
- 01_workbook\lanci_spacex_falcon.xlsx: workbook corrente dei lanci SpaceX/Falcon.
- pad_di_lancio\: cartella corrente delle infografiche pad di lancio SpaceX, aggiornata al 14/06/2026.
- Nota git: i workbook, i backup, le fonti Office, i temporanei, le cache e gli output HTML intermedi sono locali e ignorati; i sorgenti Python, HTML pubblici, immagini pubblicate, fonti e guide vanno versionati.

Nomi standard
-------------
- lanci_spacex_falcon.xlsx: workbook Falcon/SpaceX corrente, gia' spostato in 01_workbook.
- sviluppo_starship.xlsx: workbook Starship corretto; sostituisce il vecchio nome con refuso Sviluppp_starship.xlsx.
- *_backup_YYYYMMDD_HHMMSS.xlsx: formato per i backup con timestamp.

Regole importanti
-----------------
- Non modificare gli .xlsx a livello ZIP/XML.
- Per i workbook complessi usare Excel COM, salvare da Excel e verificare riaprendo in sola lettura.
- Creare sempre un backup prima di aggiornare un workbook.
- Non sovrascrivere i backup.
- Non usare file di lock tipo ~$*.xlsx come sorgenti dati.
- Per dati recenti, verificare online prima di aggiornare contenuti operativi.

Script
------
Lo script 03_script\genera_sito_rivoluzione.py genera il sito statico multipagina "Rivoluzione Spaziale". Regola importante:
- la nav globale e la homepage sono solo per il primo livello del sito: Home, SpaceX, Blue Origin, ULA, Rocket Lab, Arianespace, Cina;
- Lanci imminenti, Storico lanci, Starship, Pad di lancio e Storia sono sottosezioni di SpaceX e devono restare linkate da sezioni\spacex.html;
- Storia SpaceX vive in sezioni\storia-spacex.html come indice di parti selezionabili. Non inserire il racconto storico direttamente nella pagina porta sezioni\spacex.html;
- La prima parte storica pubblicata e' "Dalla fondazione fino al primo lancio" e punta a documenti per sito\fondazione_spacex_fino_primo_falcon1.html;
- La seconda parte storica pubblicata e' "Dal primo fallimento al quarto lancio" e punta a documenti per sito\falcon1_dal_primo_fallimento_al_quarto_lancio.html;
- La terza parte storica pubblicata e' "Dal primo successo orbitale al contratto CRS" e punta a documenti per sito\falcon1_successo_orbitale_contratto_crs.html;
- Luna, Marte, Infrastrutture orbitali e Cronologia sono pagine provvisorie non visibili nella nav globale finche' non vengono ridefinite come macro-sezioni;
- per modifiche al sito aggiornare il generatore e rigenerare, non modificare soltanto gli HTML finali.
- il sito pubblico e' servito da gh-pages; dopo modifiche pubbliche spingere main e poi main:gh-pages, quindi verificare la URL pubblica.

Lo script 03_script\genera_workbook_starship.py genera un workbook Starship partendo da due documenti Word. Cerca i sorgenti in 05_fonti_originali:
- programma_starship_spacex.docx
- ricerca_starship_1.docx

Se questi documenti non sono presenti ma 01_workbook\sviluppo_starship.xlsx esiste, lo script ricostruisce automaticamente i sorgenti Word dal workbook corrente e poi genera 01_workbook\sviluppo_starship_generato.xlsx.

Lo script 03_script\genera_infografiche_pad.py rigenera le infografiche PNG in pad_di_lancio usando Pillow, testi e asset fotografici locali. Prima di modificarlo leggere:
- 00_documentazione\README_infografiche_pad.txt
- pad_di_lancio\fonti_pad_di_lancio.md
- pad_di_lancio\assets\crediti_immagini.json

Nota licenze: per le infografiche pad le immagini NASA/USSF/NOAA/U.S. Air Force sono pubblico dominio; la foto Boca Chica OLP-1 e' CC BY-SA 4.0 e richiede attribuzione a Jenny Hautmann.

Nota sui file bloccati
----------------------
Durante il riordino del 26/05/2026 il workbook Falcon e il relativo lock Excel sono risultati temporaneamente bloccati. Dopo un secondo controllo sono stati spostati correttamente:
- 01_workbook\lanci_spacex_falcon.xlsx
- 99_temporanei\lock_excel_spacex_20250521.tmp
