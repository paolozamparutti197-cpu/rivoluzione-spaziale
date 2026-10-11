# Revisione delle figure dell’atlante SpaceX

Verifica editoriale: 11 ottobre 2026. Perimetro: tutte le 32 schede dell’atlante.

## Esito

Oltre alla fotografia Falcon Heavy già corretta, sono state sostituite 19 figure:

- Sei fotografie annotate: Falcon 9, Dragon cargo 1, Crew Dragon, Cargo Dragon 2, Super Heavy e Ship.
- Falcon 1: architettura disegnata a due stadi, con interstadio e motori collocati nelle rispettive zone. Non è presentata come fotografia o sezione costruttiva.
- Cinque circuiti propulsivi: Merlin, Kestrel, Draco, SuperDraco, Raptor.
- Cinque topologie di rete: generazioni Starlink, laser, terminali, Direct to Cell, gateway terrestri.
- Due figure con percorsi separati: energia/dati/calore nel calcolo orbitale e ritorno indipendente di Super Heavy e Ship.

Le dodici restanti figure rappresentano sequenze di processo, non anatomie dei veicoli. Sono state controllate e conservate. Gli obiettivi futuri non sono presentati come risultati già dimostrati.

## Fotografie e condizioni

I file originali non sono ritoccati: il riquadro fotografico, le inquadrature di dettaglio e le annotazioni sono elementi SVG. La fonte, l’autore e il collegamento alle condizioni sono visibili sotto ogni figura e nella pagina Metodo; sono inclusi anche nei metadati SVG.

- Falcon 9 v1.1 / CRS-3, 17 aprile 2014: SpaceX, CC0; archivio già documentato in `assets_fondazione/falcon9-2014/CREDITI.md`. Non è una foto del Block 5.
- Dragon C2+, 25 maggio 2012: NASA, identificativo iss031e071143.
- Crew Dragon Demo-2, 31 maggio 2020: NASA / Chris Cassidy, iss063e021563. Fonte: https://www.nasa.gov/image-article/spacex-crew-dragon-approaches-international-space-station-4/ . Il cono aperto e la zona di attracco sono riconoscibili; il trunk non è identificabile in questa vista.
- Cargo Dragon CRS-26, 27 novembre 2022: NASA / Expedition 68, iss068e025336. Fonte: https://www.nasa.gov/image-article/spacex-dragon-cargo-craft-approaches-space-station/ . Inquadratura di dettaglio dall’originale NASA a 5568 × 3712 pixel.
- Super Heavy Flight 5, 13 ottobre 2024: Steve Jurvetson, CC BY 2.0. Fonte: https://commons.wikimedia.org/wiki/File:SpaceX_Starship_booster_landing_approach_IFT-5.jpg . Griglia, corpo e zona propulsiva indicati separatamente.
- SN15, 2021: Lars Plougmann, CC BY-SA 2.0. Fonte: https://commons.wikimedia.org/wiki/File:Starship_SN15_flap_and_nosecone_(51437260707).jpg . La figura annotata mantiene la stessa licenza. Non è una fotografia dello scudo orbitale o della nave attuale.

Le fotografie NASA sono impiegate a scopo informativo secondo https://www.nasa.gov/nasa-brand-center/images-and-media/ . Una foto del 2021 accreditata a SpaceX trovata nell’archivio NASA è stata esclusa, perché la sola presenza sul sito NASA non dimostrava una licenza libera del fotografo terzo.

## Controlli tecnici

I motori e gli impianti nascosti non ricevono etichette sulla fotografia. I circuiti sono schemi funzionali originali basati sulle fonti delle singole schede, non copie di tavole riservate. La presentazione NASA/AIAA di Rick Ballard è usata come fonte tecnica, non riprodotta, poiché il PDF dichiara diritti riservati.

- Merlin: flussi principali verso la camera, ramo generatore di gas e scarico della turbina separato; collegamenti meccanici distinti.
- Kestrel, Draco e SuperDraco: gas di pressurizzazione verso entrambi i serbatoi; valvole di propellente su rami separati; nessuna turbopompa fittizia.
- Raptor: due precombustori, due turbine, alimentazioni incrociate e convergenza nella camera principale. Nessuna pretesa di rappresentare gli impianti proprietari completi.
- Reti: il partner mobile è un nodo terrestre, non un satellite. Antenna utente, router e gateway sono distinti. I dati sono bidirezionali; i laser non sono attribuiti a tutte le generazioni.
- Recupero Starship: dopo la separazione, nave e booster seguono percorsi differenti, non una catena unica.

## Rigenerazione e verifiche

`atlante/spacex/figure-verificate.mjs` conserva figure, punti di riferimento, descrizioni e crediti. `build.mjs` usa questi dati prima del generatore di sequenze e rifiuta nuove anatomie o circuiti privi di una figura specifica verificata. L’opzione `--sync-figure-data` allinea i metadati persistenti in `schede.json`.

I collegamenti SVG nelle pagine includono un’impronta del contenuto, così il browser non riutilizza il vecchio schema dopo un aggiornamento. Il collegamento diretto senza query continua a funzionare.

Verifiche: decodifica delle immagini e assenza di debordamento sulle 32 pagine a 1440 e 390 pixel; testi di tutti i 32 SVG entro i rispettivi riquadri; confronto visivo di tutte le figure; secondo controllo dei punti fotografici contro gli originali; rigenerazione identica a parità di sorgenti.
