# Raptor: il principio del ciclo full-flow

Tavola originale preparata l'11 ottobre 2026 per Rivoluzione Spaziale, approvata per la pubblicazione. I file pubblici si trovano in `assets/raptor-full-flow/`; questa cartella conserva i sorgenti e il materiale di verifica locale.

## Aprire il risultato

- `anteprima.html`: versione animata vettoriale, con pulsante Pausa e ingrandimento. Funziona anche aprendo direttamente il file, senza internet.
- `raptor-full-flow.gif`: una sola animazione di 6 secondi, ripetuta in continuo; 1800 × 1300 pixel, 150 fotogrammi, 25 fps costanti (40 ms per fotogramma).
- `raptor-full-flow.png`: tavola statica a 3600 × 2600 pixel.
- `raptor-full-flow.svg`: tavola statica vettoriale e modificabile.

La GIF e l'anteprima HTML rappresentano lo stesso disegno. Non sono due proposte differenti. I file `controllo-*` e la cartella `fotogrammi` servono solo alla verifica.

## Che cosa rappresenta

Il metano e l'ossigeno vengono pressurizzati da pompe distinte. La mandata del metano alimenta soprattutto il prebruciatore ricco di combustibile; una piccola parte raggiunge quello ricco di ossigeno. Lo stesso avviene, con le parti invertite, per la mandata LOX. I punti colorati sulle mandate indicano raccordi reali nello schema; i ponticelli indicano incroci senza collegamento.

I due prebruciatori producono gas di composizione diversa, non metano puro e ossigeno puro. Questi gas azionano le rispettive turbine, che muovono le pompe attraverso due alberi indipendenti. Entrambi gli scarichi delle turbine raggiungono l'iniettore della camera principale. La combustione si completa nella camera, poi i gas accelerano attraverso la gola e si espandono nell'ugello.

## Limiti da mantenere nella pubblicazione

La tavola illustra il **principio** del ciclo full-flow LOX/metano del Raptor, non la disposizione costruttiva di Raptor 1, 2 o 3. Pompe, turbine, prebruciatori, collettori e iniettore sono rappresentazioni funzionali. La suddivisione dei due gas nelle metà dell'iniettore non riproduce la disposizione reale dei suoi elementi. Non sono indicate pressioni, temperature, portate, rapporti di miscela o regimi di rotazione.

Il raffreddamento rigenerativo è mostrato in un riquadro separato: il combustibile assorbe calore dalle pareti. Questo **non** significa che sia separato nell'impianto reale. Non si pretende di ricostruire la precisa ripartizione del metano fra i canali di raffreddamento e gli altri rami del Raptor.

Il movimento rappresenta un funzionamento continuo, non la sequenza di avviamento. Numero, spaziatura e velocità delle frecce non misurano portate. Sono omessi valvole, regolazione, avviamento, pressurizzazione dei serbatoi e circuiti ausiliari. Non è una simulazione fluidodinamica.

## Fonti tecniche primarie

- [NASA, Integrated Powerhead Demonstrator](https://www.nasa.gov/news-release/new-rocket-engine-combustion-cycle-technology-testing-reaches-100-power-level/): funzionamento dei due prebruciatori e abbinamento alle turbopompe. Il dimostratore usa idrogeno/ossigeno, non è il Raptor.
- [NASA-CR-184205, Evaluation of undeveloped rocket engine cycle applications to advanced transportation](https://ntrs.nasa.gov/citations/19910021901), §2.2.2.1, pagine stampate 46–47: architettura FFSC e alimentazioni incrociate.
- [NASA/TM-2002-211982, Experimental Evaluation of a Subscale Gaseous Hydrogen/Gaseous Oxygen Coaxial Rocket Injector](https://ntrs.nasa.gov/citations/20030003786): principio dell'iniezione gas–gas nel ciclo FFSC, non geometria dell'iniettore Raptor.
- [NASA, LOX/Methane In-Space Propulsion Systems Technology Status and Gaps](https://ntrs.nasa.gov/citations/20170005557), slide 12: identificazione del Raptor come full-flow. I dati di prestazione del documento del 2017 non sono riportati.
- [SpaceX, Starship](https://new.spacex.com/vehicles/starship): propellenti metano/ossigeno e motore Raptor a combustione stadiata.
- [NASA Glenn, Rocket Laboratory, Low-Cost Engine Cooling](https://www.nasa.gov/rocket-laboratory-space-propulsion/#:~:text=Low-Cost%20Engine%20Cooling): principio del raffreddamento rigenerativo mediante combustibile criogenico.

## Immagini e diritti

Grafica e animazione sono originali: non incorporano immagini, fotografie, loghi o diagrammi di terzi. Le immagini fornite dall'utente sono state usate come riferimento del tipo di rappresentazione, senza ricopiarne i valori numerici o la geometria. Nessuna immagine viene presentata come disegno ufficiale SpaceX o NASA.

Tavola e animazione sono pubblicate con CC BY 4.0, attribuzione «Rivoluzione Spaziale, monografia Starship».

## File di costruzione

`costruisci-schema.cjs` genera il disegno e l'anteprima; `animazione.js` gestisce le frecce e le giranti; `renderizza.cjs` esporta SVG, PNG e fotogrammi con Chromium; `crea-gif.py` crea la GIF con Pillow e palette unica. Tutti i programmi operano nella propria cartella e non contengono comandi di pubblicazione o Git.

Per rigenerare: eseguire nell'ordine i tre programmi `costruisci-schema.cjs`, `renderizza.cjs` e `crea-gif.py`, con Node.js per i primi due e Python per il terzo. Il percorso di Chromium e Playwright in `renderizza.cjs` è quello del runtime di questo computer.

Dopo le verifiche, copiare soltanto `raptor-full-flow.gif` e `raptor-full-flow.svg` in `assets/raptor-full-flow/`. La GIF mantiene 150 fotogrammi da 40 ms, palette unica, giranti lente e nessuna pulsazione. Non pubblicare `fotogrammi/` o i PNG di controllo. Le due pagine usano lo stesso asset, il lettore `flow.js` e lo stile `flow.css`; il lettore rispetta la preferenza per il movimento ridotto e permette di sostituire l'animazione con lo schema statico.

## Verifiche

- Controllo indipendente dei percorsi e delle etichette rispetto alle fonti primarie.
- Controllo visivo del disegno realmente renderizzato, non soltanto del sorgente.
- Tutti i testi entro i limiti della tavola.
- Frecce sempre orientate lungo i percorsi; raccordi distinti dagli incroci.
- Pompe e turbine di ciascuna coppia ruotano insieme; i due alberi sono indipendenti.
- Giranti rallentate a una rotazione illustrativa per ciclo per evitare lo sfarfallio delle palette ripetute. Niente pulsazioni decorative o microfrecce animate sopra le palette.
- Controllo dei fotogrammi intermedi, della durata totale e della ripetizione senza salti.

Le specifiche finali della GIF sono registrate in `verifica-gif.json`; la geometria dei percorsi in `verifica-percorsi.json`.
