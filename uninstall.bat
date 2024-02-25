@echo off
setlocal enabledelayedexpansion

echo Pulizia della cartella in corso...

if exist __pycache__ (
    echo Rimozione della cartella __pycache__...
    rmdir /s /q __pycache__
)

if exist bot (
    echo Rimozione della cartella bot...
    rmdir /s /q bot
)

if exist build (
    echo Rimozione della cartella build...
    rmdir /s /q build
)

if exist dist (
    echo Rimozione della cartella dist...
    rmdir /s /q dist
)

if exist config.py (
    echo Rimozione del file config.py...
    del /q config.py
)

if exist main.spec (
    echo Rimozione del file main.spec...
    del /q main.spec
)

if exist price_tables.db (
    echo Rimozione del file price_tables.db...
    del /q price_tables.db
)

if exist start.bat (
    echo Rimozione del file start.bat...
    del /q start.bat
)

:: Rimuovi il job schedulato
schtasks /delete /tn "EseguiScriptPythonOgniGiorno" /f

echo Pulizia completata.
endlocal
