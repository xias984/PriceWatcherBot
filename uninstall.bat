@echo off
setlocal enabledelayedexpansion

echo Pulizia della cartella in corso...

if exist __pycache__ (
    echo Rimozione della cartella __pycache__...
    rmdir /s /q __pycache__
)

if exist pwb (
    echo Rimozione della cartella pwb...
    rmdir /s /q pwb
)

if exist config.py (
    echo Rimozione del file config.py...
    del /q config.py
)

if exist price_tables.db (
    echo Rimozione del file price_tables.db...
    del /q price_tables.db
)

if exist start.bat (
    echo Rimozione del file start.bat...
    del /q start.bat
)

if exist cron.log (
    echo Rimozione del file cron.log...
    del /q cron.log
)

:: Rimuovi i jobs schedulato
schtasks /delete /tn "PWB_update_prices" /f
schtasks /delete /tn "PWB_send_notify" /f

echo Pulizia completata.
endlocal
