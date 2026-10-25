# Vedute Merlin 1D, 25 ottobre 2026

La pagina `atlante/spacex/merlin.html` comprende ora quattro rendering originali: insieme a tre quarti, frontale ortografica, laterale ortografica e dettaglio del gruppo superiore. Ogni figura ha testo alternativo, spiegazione tecnica, indicazione di ciò che va osservato e collegamento alla piena dimensione.

Le funzioni sono riferite alla guida ufficiale SpaceX Falcon 2025, §2.3, pp. 8–9. La fotografia del press kit SpaceX CRS-4, p. 15, è un riferimento storico dell’aspetto esterno, non un’immagine incorporata nei rendering. Sono dichiarati i limiti delle geometrie approssimate, della scala e degli interni non modellati; il Merlin Vacuum è escluso.

Modello e vedute sono stati creati con Blender 2.93.0 LTS. Sorgenti in `prototipi/merlin-vedute/`, derivati pubblici e crediti in `assets/merlin-vedute/`. Quattro WebP pieni e quattro varianti da 640 pixel: 822.264 byte complessivi. Le quattro varianti piccole occupano insieme 156.108 byte. I dati editoriali rimangono in `schede.json`; il generatore preserva la sezione.

## Verifiche locali

- Quattro render completi, ispezionati visivamente; dimensioni controllate durante la conversione.
- Pagina verificata a 1440 e 390 pixel, con JavaScript abilitato e disabilitato: quattro casi passati, quattro immagini decodificate per caso, nessun errore di pagina o richiesta fallita, nessuna fuoriuscita orizzontale.
- Galleria desktop e mobile controllata tramite schermate del browser.
- Schema animato preesistente presente; collegamenti alle immagini e ai crediti risolti.
- Sintassi Python e modulo JavaScript controllata; `git diff --check` superato.
- Rigenerazione dell’atlante: nessuna variazione delle altre schede.

Pubblicazione prevista sui rami `main` e `gh-pages`, come indicato nel README del progetto. Le altre modifiche locali della cartella di lavoro originaria sono estranee a questo aggiornamento.
