# Merlin: circuito a generatore di gas

Tavola e animazione originali di Rivoluzione Spaziale, 11 ottobre 2026. CC BY 4.0. Nessuna immagine di terzi incorporata.

## Che cosa rappresenta

Il principio del Merlin 1D: due pompe, per LOX e RP-1, e una turbina sullo stesso albero. Piccole derivazioni dopo le pompe alimentano il generatore di gas. I gas prodotti azionano la turbina, poi vengono scaricati senza tornare nella camera principale. Il combustibile nel ramo principale assorbe calore nelle pareti prima di alimentare la combustione. L'iniettore a pintle è reso con un simbolo in sezione, non con la sua geometria reale.

L'affiancamento dei tre rotori è una convenzione grafica, non una sezione meccanica della turbopompa. I rotori condividono la fase dell'animazione perché sono sul medesimo albero. I ponti indicano incroci senza raccordo; i punti blu e verdi indicano le sole derivazioni.

Il percorso verde nella parete illustra la funzione del raffreddamento rigenerativo: non ricostruisce collettori, numero e distribuzione dei canali del Merlin. Mostrare una linea sul lato destro non significa che l'altro lato sia privo di raffreddamento. L'uscita della turbina è simbolica e non ricostruisce il suo orientamento o gli organi di controllo. La tavola non descrive la distribuzione dei gas nell'estensione dell'ugello Merlin Vacuum: l'assenza di ritorno alla **camera** non significa che, in tutte le varianti, i gas non possano essere convogliati nella zona dell'ugello.

Valvole, accensione TEA-TEB, sequenze di avviamento, spurgo e pressurizzazione sono omessi. Nessuna pressione, temperatura, portata o velocità di rotazione è stimata. Il movimento illustra un regime continuo, non la sequenza di accensione. Le dimensioni non sono in scala.

## Fonti tecniche

- [SpaceX, Falcon User's Guide, edizione 2025](https://www.spacex.com/assets/media/falcon-users-guide-2025-05-09.pdf), §2.3, pagina stampata 8 (pagina PDF 19): albero comune alle due pompe e alla turbina; ciclo a generatore di gas; camera e ugello raffreddati rigenerativamente; iniettore a pintle. Si impiegano i fatti tecnici, non le figure protette del documento.
- [NASA-CR-184205, Evaluation of undeveloped rocket engine cycle applications to advanced transportation](https://ntrs.nasa.gov/citations/19910021901), §2.1.1.1, figura 2.1-3: principio del ciclo a generatore di gas e scarico dopo la turbina. È un riferimento generale, non una sezione Merlin.
- [SpaceX/NASA, CRS-4 press kit, 2014](https://www.nasa.gov/wp-content/uploads/2018/07/spacex_nasa_crs-4_presskit.pdf), pagina 16: conferma storica della turbopompa a due giranti su un albero. Nessuna immagine del press kit viene copiata.

## Rigenerazione

Prerequisiti: Node, Playwright/Chromium nei percorsi indicati dal renderer, Python con Pillow e NumPy.

```powershell
node prototipi/merlin-ciclo-gas/costruisci-schema.cjs
node prototipi/merlin-ciclo-gas/renderizza.cjs
python prototipi/merlin-ciclo-gas/crea-gif.py
```

Per il solo poster: `node prototipi/merlin-ciclo-gas/renderizza.cjs --solo-anteprima`.

La GIF contiene 150 fotogrammi di 40 ms: 25 fps, ciclo di sei secondi. Palette unica, niente dithering, delta trasparenti e composizione con disposal 1. Tutti i fotogrammi decodificati sono confrontati pixel per pixel con i render quantizzati; titolo, legenda, bordi dei pannelli, limiti e footer devono rimanere invarianti. I quattro colori della legenda devono rimanere esatti. Il renderer verifica il ritorno pixel-identico tra t=0 e t=6.

I file di lavoro e i fotogrammi restano sul disco, esclusi da Git. Gli asset pubblici sono in `assets/merlin-ciclo-gas/`; la pagina e l'alias SVG dell'atlante si rigenerano tramite `atlante/spacex/build.mjs` e i metadati persistenti in `schede.json`.
