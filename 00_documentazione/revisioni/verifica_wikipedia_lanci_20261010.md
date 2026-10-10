# Revisione dell'elenco operativo con Wikipedia

10 ottobre 2026. Revisione successiva al terzo upgrade; supera i numeri e i perimetri descritti nel precedente rapporto di importazione.

## Risultato

713 decolli operativi abbinati uno a uno: 5 Falcon 1, 693 Falcon 9, 14 Falcon Heavy e Starship Flight 14. Nessuna missione mancante nei due elenchi entro la copertura consultata. Le tabelle Wikipedia contengono anche il lancio SDA del 10 ottobre, mentre il riepilogo introduttivo Falcon era ancora fermo al 2 ottobre: sono state usate le singole righe, non il totale introduttivo.

L'elenco principale, la ricerca predefinita e il riepilogo storico includono Starship solo quando la fase dell'Excel principale è `Operativo`, come richiesto dall'utente. Le 13 prove precedenti hanno un elenco separato e rimangono escluse dai conteggi operativi. Amos-6 resta una scheda di evento a terra, senza decollo né volo di booster. I 14 Falcon Heavy contano 14 lanci e 42 partecipazioni.

224 schede hanno correzioni documentate in 523 campi. Comprendono date UTC, sei identificativi di missione errati, booster e progressivi scambiati fra missioni vicine, pad, profili orbitali, piattaforme ed esiti di atterraggio. Gli originali sono conservati in `fonti-snapshot.json` e nei campi `before` della revisione. Le denominazioni abbreviate equivalenti non vengono sostituite.

CRS-1 è complessivamente parziale: Dragon riuscito, Orbcomm nell'orbita errata; controllo aggiuntivo sul rapporto NASA OIG IG-13-016. I successi generali operativi sono quindi 707 su 713. La revisione corregge anche IMAP (L1) e SPHEREx/PUNCH (SSO), verificati sulle fonti NASA oltre alla tabella Wikipedia. Restano 668 contatti al suolo riusciti e 631 reflight documentati. I due veicoli persi dopo un contatto riuscito non sono recuperi fisici riusciti; il numero di atterraggi non è il totale dei booster riportati integri a terra. I cinque Falcon 1 non hanno matricole e progressivi attestati dalla tabella consultata, che non vengono inventati.

La revisione non deduce gli esiti payload mancanti dal successo generale. SDA del 10 ottobre rimane privo di conferma ufficiale individuale del dispiegamento nella fonte locale; Wikipedia documenta il lancio riuscito. Le differenze fra descrizioni dei voli sperimentali Starship restano leggibili nelle schede. L'atlante non è stato modificato.

## Fonti e tracciabilità

`archivio/spacex/correzioni-wikipedia.json` conserva i 713 abbinamenti, i valori di partenza attesi, le correzioni, gli URL e gli SHA-256 delle sette pagine consultate: Falcon 1, Starship, Falcon 2010–2019, 2020–2022, 2023, 2024 e pagina principale con 2025–2026. I file HTML completi delle fonti restano nella cartella temporanea ignorata da Git, senza ripubblicare gli articoli.

La pagina pubblica `verifica-wikipedia.html` mostra il metodo, le fonti e tutti i valori prima e dopo. Ogni scheda verificata espone data e collegamento alla tabella utilizzata. Per Falcon Heavy i laterali si abbinano per matricola; A/B resta l'ordine delle righe, non il lato fisico. I progressivi senza suffisso vengono ricostruiti come primo impiego soltanto quando il veicolo compare per la prima volta nella cronologia completa Falcon consultata; la deduzione è esplicitata nella correzione.

## Compatibilità e manutenzione

Nessun Python di gestione, Excel o file dell'atlante è modificato. La revisione vive nei nuovi moduli Node `correzioni_archivio_spacex.mjs` e `riepilogo_archivio_spacex.mjs`, richiamati dal costruttore autonomo dell'archivio.

Dopo la normale rigenerazione Python e prima di pubblicare, eseguire:

```powershell
& .\03_script\aggiorna_archivio_spacex.ps1
node .\03_script\verifica_archivio_spacex.mjs
```

Il nuovo passaggio importa le fonti in sola lettura, applica la revisione, aggiorna archivio, riepilogo storico e KPI della pagina SpaceX. I Python preesistenti possono continuare a funzionare senza modifiche. La sola rigenerazione Python può ripristinare i valori grezzi nel riepilogo: per pubblicare i numeri rivisti va eseguito anche il passaggio autonomo qui sopra. L'archivio rimane una fotografia esplicitamente datata.

Se una fonte modifica un valore verificato, le precondizioni interrompono la costruzione prima delle scritture; occorre rivedere la revisione. Le nuove missioni non vengono dichiarate automaticamente verificate da Wikipedia. Le pagine vengono scritte solo quando cambiano, attraverso file temporanei e sostituzione, per evitare troncamenti mentre Windows le indicizza.

## Verifiche

- Abbinamenti unici: 713 missioni operative, nessun record senza corrispondenza; confronto di ogni campo corretto con il risultato pubblicato.
- Rifiuto di una modifica deliberata del nome della fonte; applicazione ripetibile della revisione, senza cambiare gli originali.
- Esiti, date, identificativi, tre ruoli Falcon Heavy e separazione delle prove Starship verificati dai controlli dell'archivio.
- Excel letti indipendentemente in sola lettura: 742 righe elenco, due recuperi, 11 siti e 14 voli integrati.
- SHA-256 dei 112 file protetti invariati: 21 Python preesistenti nella cartella script, 77 file dell'atlante, Excel e modifiche utente già presenti.
- Verifica browser desktop e mobile, filtri, conteggi, esportazioni CSV/JSON, schede, elenchi statici e pagina delle correzioni; controllo dei riferimenti locali.

Pubblicazione sui rami `main` e `gh-pages`, con verifica del workflow relativo al commit pubblicato e confronto delle risorse online con i file locali prima dello spegnimento richiesto dall'utente.
