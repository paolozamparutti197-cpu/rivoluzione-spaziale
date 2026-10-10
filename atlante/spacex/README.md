# Atlante tecnico SpaceX

Questa cartella è una sezione statica autonoma del sito. Le pagine HTML, CSS, JavaScript e SVG sono già pronte per GitHub Pages e non richiedono modifiche o nuovi passaggi nei Python e nei batch di manutenzione esistenti.

La fonte delle schede è `schede.json`: testi, dati con configurazione e data, fonti, riferimenti alle fotografie già presenti nelle monografie, collegamenti di approfondimento e descrizioni degli schemi. I crediti fotografici vengono conservati anche nelle singole pagine.

Per aggiornare l'atlante: modificare `schede.json`, poi eseguire dalla cartella del progetto `node atlante/spacex/build.mjs`. Il generatore usa soltanto librerie native Node e scrive esclusivamente in questa cartella. Pubblicare anche i file generati. Non viene richiamato dai Python: un normale aggiornamento dei lanci conserva l'atlante già pubblicato.

I rimandi nei libri sono conservati nelle rispettive sorgenti `monografie/<libro>/contenuti/`. Le normali rigenerazioni dei libri mantengono i collegamenti. L'accesso principale è nella pagina manuale `sezioni/monografie-spacex.html`, che non viene sovrascritta dal generatore generale.

Edizione iniziale: 10 ottobre 2026. Verifiche e inventario: `00_documentazione/revisioni/atlante_spacex_20261010.md`.
