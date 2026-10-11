# Circuito animato Merlin

Tavola e GIF originali di Rivoluzione Spaziale, 11 ottobre 2026, CC BY 4.0. Nessuna grafica di terzi incorporata.

Fonti: [SpaceX, Falcon User's Guide 2025](https://www.spacex.com/assets/media/falcon-users-guide-2025-05-09.pdf), §2.3, p. 8; [NASA-CR-184205](https://ntrs.nasa.gov/citations/19910021901), §2.1.1.1 e figura 2.1-3.

Schema funzionale, non costruttivo: un generatore di gas, una turbina, due pompe sul medesimo albero. Scarico turbina distinto dalla camera principale. Camicia rigenerativa e iniettore simbolici; nessuna ricostruzione dei condotti del Merlin Vacuum. Omesse valvole, accensione e circuiti ausiliari; geometria e velocità illustrative.

Sorgenti riproducibili e controlli nel progetto: `prototipi/merlin-ciclo-gas/`. La GIF usa 150 frame di 40 ms, palette unica e ciclo continuo di sei secondi. Ogni fotogramma decodificato viene controllato pixel per pixel. Testi e legenda rimangono fissi.

Il lettore accessibile condiviso resta in `assets/raptor-full-flow/flow.js` e `flow.css`: la classe storica è riutilizzata senza duplicare codice. Poster statico senza JavaScript o con movimento ridotto, avvio manuale, ingrandimento e scorrimento interno sui telefoni. L'atlante conserva l'animazione tramite i suoi dati e il generatore persistenti.
