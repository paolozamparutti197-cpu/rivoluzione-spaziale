# Revisione SpaceX, 10 ottobre 2026

## Vincolo e metodo

Richiesta: primo prompt di per110.md; nessuna modifica ai Python che gestiscono il progetto.
Inventario iniziale: 157 HTML pubblici (114 monografie, 30 capitoli/dossier, 12 sezioni, 1 home).
Controllo editoriale del perimetro, riscontri mirati primari, controlli locali e diagnostica esterna.
Questo rapporto non certifica ogni affermazione né riconcilia autonomamente tutti i 714 lanci.

## Persistenza

- Pagine autonome in documenti per sito: correzioni negli HTML mantenuti manualmente.
- Monografie: correzioni nei contenuti e fonti JSON, output rigenerati con i generatori esistenti.
- Rapporto pubblico collegato dall’indice manuale delle monografie e dai sorgenti degli indici dei cinque libri.
- Pagine generali prodotte da genera_sito_rivoluzione.py: non modificate direttamente con correzioni che andrebbero perdute. I limiti semantici della dashboard sono spiegati nel rapporto pubblico.
- Nessun hook, nuova dipendenza o modifica alle procedure di gestione. I soli programmi di verifica della sessione sono temporanei e ignorati da Git.

## Correzioni e questioni aperte

Il registro leggibile è documenti per sito/revisione_spacex_20261010.html.
La fonte NASA/SP-2014-617 è stata letta: PDF p. 66, numerazione stampata p. 58, 396 milioni NASA e circa 454 SpaceX, perimetro COTS.
SES-8 press kit p. 3 (PDF p. 4): 3138 kg e profilo previsto 295 × 80000 km; Annual Report SES 2013 p. 6: lancio 3 dicembre.
La fotografia del recupero C2+ è NASA/US Navy; Commons registra modifica del contrasto.
Le fotografie già documentate nelle monografie sono conservate; nessuna nuova immagine sintetica viene usata come evidenza.

## Statistiche, controllo in sola lettura

01_workbook/lanci_spacex.xlsx: valori salvati e formule letti senza scrittura né ricalcolo.
dashboard A4: 714; C4: 708; E4: circa 0,9915966; I7: 668; K7: 613; K4: 5.
Righe principali: 694 Falcon 9, 14 Falcon Heavy, 5 Falcon 1 e 1 Starship.
K7 somma il flag booster_riutilizzato; il flag vale 1 se il numero di voli è almeno 2: non è il conteggio di matricole distinte.
K4 conta pad con lanci nella serie e ID diverso da PAD-TBD: non la disponibilità operativa attuale.
I7 include righe tecniche dei booster, necessarie per rappresentare Falcon Heavy.

## Materiali della sessione

99_temporanei/revisione110 conserva inventario, diagnostica, baseline SHA256 dei Python, modifiche editoriali, fonti PDF e risultati delle verifiche.
I file temporanei non fanno parte della pubblicazione.
Il dossier Q2 2026 aveva modifiche precedenti: non è stato modificato o incluso nel commit di questa revisione.
Le altre modifiche precedenti in README e documentazione, e i file non tracciati già presenti, restano fuori dal commit.

## File editoriali modificati

- documenti per sito/fondazione_spacex_fino_primo_falcon1.html
- documenti per sito/fondazione_spacex_fino_primo_falcon1.html
- documenti per sito/falcon1_dal_primo_fallimento_al_quarto_lancio.html
- documenti per sito/falcon1_dal_primo_fallimento_al_quarto_lancio.html
- documenti per sito/falcon9_salto_scala_cots1.html
- documenti per sito/falcon9_salto_scala_cots1.html
- documenti per sito/dragon_c2plus_attracco_iss.html
- documenti per sito/amos6_disastro_indagine_ripartenza_2016.html
- documenti per sito/falcon9_2017_riutilizzo_accelerazione.html
- documenti per sito/falcon9_v11_mercato_riuso_2013.html
- documenti per sito/spacex_crew12_ritorno.html
- documenti per sito/spacex_allhands_agosto_2026.html
- documenti per sito/spacex_allhands_agosto_2026.html
- documenti per sito/spacex_louisiana_pecan_island.html
- documenti per sito/spacex_s40_christmas_island.html
- documenti per sito/spacex_ship40_ritorno_starbase.html
- monografie/crew-dragon/contenuti/12-presente-futuro.html
- monografie/starship/contenuti/21-hls.html
- monografie/starship/contenuti/19-riutilizzo.html
- monografie/starlink/fonti.json
- monografie/starship/fonti.json
- monografie/crew-dragon/contenuti/indice.html
- monografie/starlink/contenuti/indice.html
- monografie/starship/contenuti/indice.html
- monografie/artemis/contenuti/indice.html
- monografie/starmind/contenuti/indice.html
- sezioni/monografie-spacex.html
- documenti per sito/falcon1_successo_orbitale_contratto_crs.html
- documenti per sito/spacex_falcon9_impatto_luna.html
- documenti per sito/spacex_falcon_heavy_roman.html
- documenti per sito/spacex_starbase_louisiana.html

## Verifiche finali

- Controllo strutturale iniziale su 157 pagine: nessun riferimento locale assente, nessun ID duplicato o immagine senza alt.
- Browser Chromium: 158 pagine, desktop 1440 e telefono 390 px. Nessun errore JavaScript. Le griglie Louisiana e un riferimento ai crediti Starlink Mobile causavano overflow: corretti nelle pagine autonome.
- Fotografie locali: lettura e decodifica valide. Avvisi transitori del controllo simultaneo risolti con decode e verifica mirata.
- Confronto dei 28 file Python con SHA256 iniziale: nessuna modifica.
- Rigenerazione ripetuta delle cinque monografie: output identico byte per byte.
- FAA 2018 Compendium: appendice 2, pp. 99–104, PDF pp. 105–110, 18 Falcon 9 nel manifesto 2017. Le sole missioni FAA-licensed sono 17: perimetro diverso dal totale.
- Nuovo rapporto pubblico incluso nel controllo finale; i frammenti contenuti/*.html sono template, con URL relativi alla destinazione generata, e non vengono trattati come pagine pubbliche autonome.

- Correzione visuale e collegamento ai crediti anche in documenti per sito/spacex_starlink_mobile_spettro.html.

Controllo conclusivo: 28 pagine pubbliche modificate, 56 aperture desktop/mobile, zero errori JavaScript, immagini locali decodificate, nessun overflow. Collegamenti e ancore locali delle 28 pagine: nessun errore.
