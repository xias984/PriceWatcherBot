@echo off
setlocal enabledelayedexpansion

:: Installo DB
set "DATABASE_PATH=price_tables.db"
set "SQL_FILE_PATH=price_tables.sql"

if exist "%DATABASE_PATH%" (
    echo Il file del database esiste già.
) else (
    echo Creazione del database da %SQL_FILE_PATH%...
    sqlite3 "%DATABASE_PATH%" < "%SQL_FILE_PATH%"
    echo Database creato.
)


:: Installo il virtual environment
set "VENV_NAME=bot"
set "VENV_PATH=%PROJECT_DIR%%VENV_NAME%"
set "VENV_SCRIPTS_PATH=%VENV_PATH%\Scripts"

python -m venv "%VENV_NAME%"
echo Ambiente virtuale "%VENV_NAME%" creato con successo.

:: Modifica il file amazonify.py nel virtual environment
set "FILE_PATH=%VENV_PATH%\Lib\site-packages\amazonify.py"

if exist "%FILE_PATH%" (
    echo Modifica in corso di "%FILE_PATH%"...
    powershell -Command "(Get-Content '%FILE_PATH%').replace('from urlparse import urlparse, urlunparse', 'from urllib.parse import urlparse, urlunparse') | Set-Content '%FILE_PATH%'"
    echo Sostituzione effettuata con successo.
) else (
    echo Il file specificato non esiste: "%FILE_PATH%"
)

:: Aggiornamento di pip nel virtual environment e installazione delle dipendenze
set "REQUIREMENTS_PATH=%PROJECT_DIR%requirements.txt"

"%VENV_SCRIPTS_PATH%\python.exe" -m pip --version > nul 2>&1
if %errorlevel% neq 0 (
    echo pip non trovato nel virtual environment. Assicurati che Python e pip siano installati correttamente.
    exit /b 1
)

echo Aggiornamento di pip nel virtual environment...
"%VENV_SCRIPTS_PATH%\python.exe" -m pip install --upgrade pip

if exist "%REQUIREMENTS_PATH%" (
    echo Installazione delle dipendenze nel virtual environment da %REQUIREMENTS_PATH%...
    "%VENV_SCRIPTS_PATH%\python.exe" -m pip install -r "%REQUIREMENTS_PATH%"
) else (
    echo Il file %REQUIREMENTS_PATH% non esiste.
)

:: Modifica il file amazonify.py nel virtual environment
set "FILE_PATH=%VENV_PATH%\Lib\site-packages\amazonify.py"

if exist "%FILE_PATH%" (
    echo Modifica in corso di "%FILE_PATH%"...
    powershell -Command "(Get-Content '%FILE_PATH%').replace('from urlparse import urlparse, urlunparse', 'from urllib.parse import urlparse, urlunparse') | Set-Content '%FILE_PATH%'"
    echo Sostituzione effettuata con successo.
) else (
    echo Il file specificato non esiste: "%FILE_PATH%"
)

:: Imposto il job pianificato
set "PROJECT_DIR=%~dp0"
schtasks /create /sc daily /tn "EseguiScriptPythonOgniGiorno" /tr "python \"%PROJECT_DIR%cron_update_prices.py\"" /st 05:00
echo Task schedulato correttamente.

:: Esegui main.py utilizzando l'interprete Python dell'ambiente virtuale
echo Esecuzione di main.py nel virtual environment...
"%VENV_SCRIPTS_PATH%\python.exe" "%PROJECT_DIR%main.py"

echo Script main.py eseguito.

endlocal
