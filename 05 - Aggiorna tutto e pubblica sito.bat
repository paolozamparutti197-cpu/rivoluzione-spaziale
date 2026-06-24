@echo off
setlocal
title Rivoluzione Spaziale - Aggiornamento completo

cd /d "%~dp0"
set "PYTHON=C:\Python314\python.exe"

echo ============================================================
echo  RIVOLUZIONE SPAZIALE - AGGIORNAMENTO COMPLETO
echo ============================================================
echo.

if not exist "%PYTHON%" (
    echo ERRORE: Python non trovato in:
    echo %PYTHON%
    goto :errore
)

if not exist "03_script\aggiorna_lanci_spacex_sito.py" (
    echo ERRORE: script dei prossimi lanci non trovato.
    goto :errore
)

if not exist "03_script\genera_sito_rivoluzione.py" (
    echo ERRORE: generatore dello storico Excel non trovato.
    goto :errore
)

if not exist "electronlab\aggiorna_lanci_electron_sito.py" (
    echo ERRORE: script dei prossimi lanci Electron non trovato.
    goto :errore
)

echo 1. Scarico i prossimi lanci Electron dal web.
echo 2. Scarico i prossimi lanci SpaceX dal web.
echo 3. Rigenero il sito e gli storici usando i file Excel.
echo 4. Pubblico le modifiche su main e gh-pages.
echo.

"%PYTHON%" "electronlab\aggiorna_lanci_electron_sito.py"
if errorlevel 1 goto :errore

"%PYTHON%" "03_script\aggiorna_lanci_spacex_sito.py" --publish
if errorlevel 1 goto :errore

echo.
echo ============================================================
echo  AGGIORNAMENTO E PUBBLICAZIONE COMPLETATI
echo ============================================================
echo.
echo Pagina prossimi lanci:
echo https://paolozamparutti197-cpu.github.io/rivoluzione-spaziale/sezioni/lanci-imminenti.html
echo.
echo Pagina storico lanci:
echo https://paolozamparutti197-cpu.github.io/rivoluzione-spaziale/sezioni/storico-lanci.html
echo.
echo Pagina Electron Lab:
echo https://paolozamparutti197-cpu.github.io/rivoluzione-spaziale/sezioni/electron-lab.html
echo.
pause
exit /b 0

:errore
echo.
echo ============================================================
echo  AGGIORNAMENTO INTERROTTO: CONTROLLA L'ERRORE QUI SOPRA
echo ============================================================
echo.
pause
exit /b 1
