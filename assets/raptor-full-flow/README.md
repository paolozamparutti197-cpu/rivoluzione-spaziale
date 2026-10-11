# Ciclo Raptor: tavola animata condivisa

Edizione 11 ottobre 2026. Tavola e animazione originali di Rivoluzione Spaziale, CC BY 4.0, attribuzione «Rivoluzione Spaziale, monografia Starship».

`raptor-full-flow.gif` contiene 150 fotogrammi da 40 ms (6 secondi, ripetizione continua). `raptor-full-flow.svg` è il poster vettoriale. `flow.js` e `flow.css` gestiscono avvio/arresto, ingrandimento, caricamento quando visibile e preferenza per il movimento ridotto. Arrestare il movimento significa mostrare il poster, non sospendere la GIF su un fotogramma. Senza JavaScript resta disponibile lo schema statico.

La figura illustra il principio FFSC LOX/metano, non la disposizione costruttiva di una versione Raptor. Geometrie, flussi e velocità sono illustrative; il riquadro del raffreddamento è separato soltanto nella rappresentazione. Le due metà dell'iniettore sono simboliche. Non sono riportati parametri stimati di pressione, temperatura o portata.

Fonti tecniche: [NASA-CR-184205](https://ntrs.nasa.gov/citations/19910021901), [iniezione gas–gas NASA](https://ntrs.nasa.gov/citations/20030003786), [NASA LOX/metano](https://ntrs.nasa.gov/citations/20170005557), [IPD](https://www.nasa.gov/news-release/new-rocket-engine-combustion-cycle-technology-testing-reaches-100-power-level/), [raffreddamento NASA Glenn](https://www.nasa.gov/rocket-laboratory-space-propulsion/), [SpaceX Starship](https://new.spacex.com/vehicles/starship). Il dimostratore IPD e la ricerca sull'iniezione citata usano idrogeno/ossigeno: documentano principi, non dettagli del Raptor.

I sorgenti riproducibili sono in `prototipi/raptor-full-flow/`. Gli inserimenti persistenti risiedono nel frammento `monografie/starship/contenuti/06-raptor-ciclo.html` e nel generatore `atlante/spacex/build.mjs`, con metadati in `schede.json`. Non correggere soltanto gli HTML generati.
