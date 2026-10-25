# Revisione e ampliamento della monografia Merlin

25 ottobre 2026. Versione di confronto: commit `229b140`.

Il testo è passato da **1.356 a 4.029 parole**. Escludendo la bibliografia ne restano **3.581**; i tredici capitoli tecnici contengono 2.651 parole, cui si aggiungono introduzione, dati, didascalie e spiegazioni delle vedute. Menu, indice, comandi del lettore e numeri dei rimandi alle fonti sono esclusi dal conteggio. Apostrofi e trattini interni non dividono una parola.

Le aggiunte riguardano storia 1A/1C/1D, Fastrac e pintle, alimentazione e pressurizzazione, ciclo, turbopompa e vibrazioni, materiali della camera, flusso nell’ugello, spinta e impulso specifico, regolazione, MVac, controllo del veicolo, prove di accettazione, anomalia del 2020 e manutenzione del singolo motore.

L’inventario `merlin_incremento_informativo_20261025.json` enumera 30 punti preesistenti e 24 aggiunte verificate e collegate a una fonte. L’incremento dell’inventario è dell’80%, superiore al minimo richiesto del 20%. È un criterio editoriale esplicito, non una misura assoluta dell’informazione. Le ripetizioni, le riformulazioni e la sola crescita delle parole non valgono come aggiunte. Il controllo automatico verifica la presenza dei passi e dei riferimenti; il confronto fra contenuti e fonti è stato svolto durante la revisione.

La prosa è stata rivista secondo la skill stile-paolo: periodi con soggetti concreti, punteggiatura ordinaria, meno richiami generici e ripetizioni; nessuna enfasi promozionale o conclusione di circostanza. Sono stati accorciati anche alcuni passaggi che ripetevano i limiti delle immagini. Le caratteristiche documentate rimangono distinte dalle geometrie approssimate del modello.

## Verifiche

- Conteggio ripetibile tramite `prototipi/merlin-vedute/verifica_editoriale.py`, con confronto al commit precedente e controllo dell’inventario.
- Tredici capitoli e tredici voci di indice; rimandi numerati alle fonti risolti, quattro vedute conservate.
- Browser a 1440 e 390 pixel, con e senza JavaScript: quattro casi passati, immagini decodificate, nessun errore o richiesta fallita, nessuna fuoriuscita orizzontale.
- Larghezza del testo limitata a 820 pixel; indice e due campioni dei capitoli ispezionati tramite schermate desktop e mobile.
- Sintassi del modulo e `git diff --check` verificati. La correzione della data della fonte NASA del gennaio 2021 aggiorna anche il relativo riferimento della pagina McGregor; l’indice dell’atlante riflette la nuova descrizione Merlin.

Sorgente dei capitoli: `atlante/spacex/merlin-articolo.json`. Metadati, didascalie e fonti: `schede.json`. La rigenerazione dell’atlante conserva il testo e le figure.
