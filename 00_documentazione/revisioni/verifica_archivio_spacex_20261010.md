# Terzo upgrade: archivio missioni SpaceX

10 ottobre 2026. Nuova sezione statica `archivio/spacex`, collegata dall'ingresso persistente Programmi e monografie. L'atlante è rimasto invariato.

## Risultato

727 schede: 726 decolli e un evento pre-lancio (Amos-6). Le fonti contengono 714 record principali, 28 record di booster aggiuntivi e 14 voli integrati Starship. Il volo 14 è unito per numero, famiglia e data: non viene contato due volte. 14 Falcon Heavy corrispondono a 14 lanci e 42 partecipazioni di booster.

Ricerca con filtri combinabili, collegamenti alle singole missioni, paginazione, URL della ricerca, statistiche con formule e copertura, grafici annuali e mensili, confronto di anni con uguale parte dell'anno, CSV missioni, CSV veicoli/recuperi, CSV serie annuali, JSON con filtri e provenienza. Le schede e l'indice completo funzionano anche senza JavaScript.

## Riconciliazione e limiti

- Il vecchio riepilogo conta 714 lanci, includendo Amos-6. La nuova vista distingue 713 decolli principali e la prova a terra Amos-6, senza cambiare l'Excel. Fonte della correzione: comunicato SpaceX conservato dalla NASA, https://sma.nasa.gov/LaunchVehicle/assets/anomaly-updates-spacex.pdf.
- Restano riconciliati 708 successi generali e 668 atterraggi dei booster nei record principali e loro righe tecniche.
- Il flag Excel riutilizzato vale 613; i reflight con progressivo documentato sono 612 nello stesso perimetro. Transporter-11 ha il flag riutilizzato ma matricola e progressivo N/A: segnalato, senza riempire i campi mancanti.
- Un solo esito payload è compilato esplicitamente nell'Excel lanci. Gli altri restano mancanti: il generico successo del lancio non è una conferma del carico.
- I testi Starship con criteri di esito diversi vengono mostrati affiancati. Il recupero fisico di Ship S40 proviene dalle note dell'Excel sviluppo, non è una deduzione dall'ammaraggio.
- Le fonti individuali web sono quelle dei registri originali. La verifica di importazione e coerenza non costituisce verifica indipendente di tutte le 727 missioni. La pagina ufficiale associata al volo 14 non ha restituito testo leggibile durante il controllo.

## Verifiche eseguite

1. Confronto indipendente con openpyxl in sola lettura di tutte le righe e i campi importati: 742 righe elenco, 2 recuperi, 11 siti, 14 prove integrate. Nessuna divergenza di valori.
2. Hash di 112 file protetti invariati, inclusi 21 Python preesistenti nella cartella script, 77 file dell'atlante, Excel e modifiche utente preesistenti. Nessun Python tracciato presenta differenze Git.
3. Controlli automatici: duplicati, legami missione/tentativo/lancio, tre ruoli Falcon Heavy, matricole duplicate nello stesso lancio, progressivi, flag, recupero senza tentativo, date invalide/future e doppio conteggio Starship. Le incoerenze dei progressivi già presenti sono segnalate senza sostituzione.
4. Casi di verifica del conteggio Falcon Heavy, degli esiti mancanti, di Amos-6, dei recuperi sperimentali, della ricerca combinata e delle serie annuali. Mutazioni deliberatamente errate vengono rifiutate. Confronto di anni bisestili verificato.
5. Browser Chromium: desktop e mobile 390 px, ricerca, filtri, CSV e JSON effettivamente scaricati e confrontati con il sottoinsieme Falcon Heavy, schede, evento pre-lancio, paginazione e confronto degli anni. Nessun errore JavaScript o HTTP. Larghezza mobile entro la viewport.
6. 731 pagine HTML controllate: nessun riferimento locale mancante. Anteprime desktop e mobile ispezionate.
7. Aggiornamento completo con il nuovo PowerShell eseguito due volte: fonti aperte in sola lettura, gestori Python senza modifiche, registro delle segnalazioni conservato.

## Manutenzione

Il normale aggiornamento Python non cancella la nuova sezione; non ne aggiorna automaticamente la fotografia. Per importare nuovi dati, dopo la normale rigenerazione del sito eseguire `03_script/aggiorna_archivio_spacex.ps1`, quindi `node 03_script/verifica_archivio_spacex.mjs`. Node deve essere disponibile, oppure specificato con `-NodeExe`. Nessuna nuova libreria o modifica ai Python è richiesta. La data della fotografia è sempre esposta al lettore.

La pubblicazione viene effettuata sui rami main e gh-pages. La verifica online controlla l'esito del workflow relativo al nuovo commit e confronta le risorse pubblicate con quelle locali.
