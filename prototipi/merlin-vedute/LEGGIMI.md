# Vedute Merlin 1D

Quattro immagini originali per `atlante/spacex/merlin.html`, create con Blender 2.93.0 LTS: insieme a tre quarti, frontale ortografica, laterale ortografica e dettaglio superiore. Il modello è una ricostruzione visiva esterna; non è un CAD SpaceX.

`base_merlin.py` ricostruisce la scena dal sorgente. `renderizza_vedute.py` apre il modello e cambia la camera senza modificare il file di partenza. La collezione delle scritte del rendering iniziale è esclusa dalle quattro vedute. I PNG sono convertiti in WebP a dimensione piena e in una variante larga 640 pixel con `prepara_immagini.py`; non vengono ritagliati o ritoccati.

Esempio PowerShell dalla radice del repository:

```powershell
$env:MERLIN_SKIP_RENDER='1'
& 'C:\Program Files\Blender Foundation\Blender 2.93\blender.exe' --background --factory-startup --python 'prototipi\merlin-vedute\base_merlin.py'
& 'C:\Program Files\Blender Foundation\Blender 2.93\blender.exe' --background 'prototipi\merlin-vedute\Merlin_1D_Blender_2.93.blend' --python 'prototipi\merlin-vedute\renderizza_vedute.py'
python 'prototipi\merlin-vedute\prepara_immagini.py'
node 'atlante\spacex\build.mjs'
```

La conversione richiede Pillow. `schede.json` conserva testi, didascalie, testo alternativo e percorsi. `render-views.mjs` e `merlin-vedute.css` costruiscono la sezione senza introdurre dipendenze JavaScript nel lettore: le quattro figure sono accessibili anche senza script. Il collegamento di ciascuna figura apre il WebP a piena dimensione.

Fonti e limiti: `assets/merlin-vedute/CREDITI.md`. I file intermedi e le scene Blender non fanno parte della pubblicazione; i sorgenti permettono di ricrearli.
