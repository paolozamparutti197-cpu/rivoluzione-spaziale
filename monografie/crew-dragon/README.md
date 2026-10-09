# Monografia Crew Dragon

Piccolo libro HTML autonomo, in dodici capitoli. Prima edizione: 9 ottobre 2026.

Aprire index.html. I capitoli, l’archivio e i crediti funzionano come pagine statiche. I video esterni richiedono la rete.

## Modifiche editoriali

I frammenti HTML in contenuti sono la fonte dei capitoli. Gli HTML di lettura sono salvati nella cartella principale dopo ogni gruppo di capitoli.

Rigenerare soltanto il libro:

```powershell
python -X utf8 03_script/genera_monografia_crew_dragon.py
```

Il comando parte dalla radice del progetto. Non modifica le altre sezioni o gli archivi dei lanci Falcon.

voli.json contiene il registro orbitale. Il generatore produce la tabella e registro-voli.csv. Le date sono UTC, le prove suborbitali restano fuori dai totali orbitali. Crew-9 deve conservare equipaggi distinti al lancio e al ritorno.

Per le immagini consultare CREDITI.md e immagini.json. L’acquisizione dei media selezionati è riproducibile con 03_script/scarica_immagini_crew_dragon.py; non sostituire una foto NASA con una foto di terzi senza verificare i diritti.

Il libro è collegato da sezioni/monografie-spacex.html, dalla sezione SpaceX, dall’indice storico e dalla conclusione Block 5. I collegamenti delle pagine generate sono riportati anche in 03_script/genera_sito_rivoluzione.py.
