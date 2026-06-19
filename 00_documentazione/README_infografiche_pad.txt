Infografiche pad di lancio SpaceX
=================================

Stato aggiornamento
-------------------
- Aggiornato al: 14/06/2026.
- Cartella operativa: pad_di_lancio.
- Script rigenerabile: 03_script\genera_infografiche_pad.py.
- File fonti e crediti immagini: pad_di_lancio\fonti_pad_di_lancio.md e pad_di_lancio\assets\crediti_immagini.json.

Contenuto prodotto
------------------
Il 14/06/2026 e' stata creata la sottocartella pad_di_lancio e vi e' stata spostata l'infografica originale:
- pad_di_lancio\pad 37b.png

Sono state poi create sei infografiche nello stesso stile grafico del 37B:
- pad_di_lancio\pad_slc-40.png
- pad_di_lancio\pad_lc-39a.png
- pad_di_lancio\pad_slc-4e.png
- pad_di_lancio\pad_slc-6.png
- pad_di_lancio\pad_boca_chica_pad_1.png
- pad_di_lancio\pad_boca_chica_pad_2.png

Formato e stile
---------------
- Tutte le immagini sono PNG verticali 1055 x 1491 px.
- Stile: fondo scuro fotografico/industriale, titolo grande, sottotitolo, box localita/nome completo, timeline a sinistra, box "FASE ATTUALE" in basso a destra, accenti ciano.
- Il layout, i testi e la struttura sono gestiti dallo script Python.
- Le foto reali dei pad sono integrate come sfondo trasparente nella parte bassa, seguendo il modello estetico dell'infografica SLC-37B.

Asset immagini
--------------
Gli asset fotografici scaricati sono in:
- pad_di_lancio\assets

Mappatura asset -> infografica:
- slc40.jpg -> pad_slc-40.png
- lc39a.jpg -> pad_lc-39a.png
- slc4e.jpeg -> pad_slc-4e.png
- slc6.jpg -> pad_slc-6.png
- boca1.jpg -> pad_boca_chica_pad_1.png
- boca2.jpg -> pad_boca_chica_pad_2.png

Licenze immagini
----------------
- SLC-40: NASA Images / SpaceX staff, pubblico dominio.
- LC-39A: NASA / Kim Shiflett, pubblico dominio.
- SLC-4E: U.S. Space Force / Michael Peterson, pubblico dominio.
- SLC-6: U.S. Air Force / Joe Davila, pubblico dominio.
- Boca Chica Pad 1 / OLP-1: Jenny Hautmann, CC BY-SA 4.0.
- Boca Chica Pad 2 / OLP-2: NOAA / NODD, pubblico dominio.

Nota importante: mantenere sempre l'attribuzione per la foto OLP-1 di Jenny Hautmann se l'infografica viene riutilizzata o pubblicata.

Fonti contenuto
---------------
Le fonti principali sono riportate in pad_di_lancio\fonti_pad_di_lancio.md. In sintesi:
- NASA per LC-39A, storia Apollo/Shuttle e lease SpaceX.
- Space Launch Delta 45 per SLC-40 e Crew-9.
- SpaceX per missioni Falcon/Starship e pagine missione.
- DAF/Space Launch Delta 30/Vandenberg per SLC-4E e SLC-6.
- FAA e Federal Register per Boca Chica, LC-39A Starship e autorizzazioni ambientali.
- Wikimedia Commons solo per immagini con licenza verificabile.

Rigenerazione
-------------
Per rigenerare le sei infografiche nuove:
1. Verificare che gli asset esistano in pad_di_lancio\assets.
2. Eseguire:
   python 03_script\genera_infografiche_pad.py
3. Lo script sovrascrive le sei PNG generate, ma non modifica pad_di_lancio\pad 37b.png.

Attenzione:
- Lo script non scarica automaticamente nuovi asset dal web; usa quelli gia' presenti in pad_di_lancio\assets.
- Se si cambiano fonti o foto, aggiornare anche:
  - pad_di_lancio\fonti_pad_di_lancio.md
  - pad_di_lancio\assets\crediti_immagini.json
  - questo file
  - 00_documentazione\storico_sessioni_lavoro.txt

Stato ricerca al 14/06/2026
---------------------------
- SLC-40: documentato come pad Falcon 9 ad alta cadenza, con torre Dragon e LZ-40.
- LC-39A: documentato come pad storico Apollo/Shuttle, lease SpaceX, Falcon Heavy/Crew Dragon e percorso Starship analizzato dalla Final EIS FAA 2026.
- SLC-4E: documentato come pad Falcon 9 della costa ovest per orbite polari/SSO, associato a LZ-4.
- SLC-6: documentato come futuro secondo pad SpaceX a Vandenberg per Falcon 9/Falcon Heavy, con ROD DAF 2025.
- Boca Chica Pad 1 / OLP-1: documentato come primo pad orbitale Starship/Super Heavy, con Flight 1, upgrades post-IFT-1, catch Flight 5 e cadenza FAA fino a 25/anno.
- Boca Chica Pad 2 / OLP-2: documentato come seconda rampa Starship per ridondanza e V3/Block 3, con primo uso indicato da SpaceX per Flight 12.
