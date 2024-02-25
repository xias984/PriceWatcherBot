#!/bin/bash

# Imposta il percorso del progetto alla directory corrente
PROJECT_DIR=$(pwd)

# Installo DB
DATABASE_PATH="${PROJECT_DIR}/price_tables.db"
SQL_FILE_PATH="${PROJECT_DIR}/price_tables.sql"

if [ -f "$DATABASE_PATH" ]; then
    echo "Il file del database esiste già."
else
    echo "Creazione del database da $SQL_FILE_PATH..."
    sqlite3 "$DATABASE_PATH" < "$SQL_FILE_PATH"
    echo "Database creato."
fi

# Imposto il job pianificato (cron job)
(crontab -l 2>/dev/null; echo "0 5 * * * python ${PROJECT_DIR}/cron_update_prices.py") | crontab -
echo "Task schedulato correttamente."

# Installo il virtual environment
VENV_NAME="bot"
python3 -m venv "${PROJECT_DIR}/${VENV_NAME}"
echo "Ambiente virtuale '${VENV_NAME}' creato con successo."

# Modifica il file amazonify.py nel virtual environment
FILE_PATH="${PROJECT_DIR}/${VENV_NAME}/lib/python3.x/site-packages/amazonify.py"

if [ -f "$FILE_PATH" ]; then
    echo "Modifica in corso di $FILE_PATH..."
    sed -i 's/from urlparse import urlparse, urlunparse/from urllib.parse import urlparse, urlunparse/' "$FILE_PATH"
    echo "Sostituzione effettuata con successo."
else
    echo "Il file specificato non esiste: $FILE_PATH"
fi

# Aggiornamento di pip nel virtual environment e installazione delle dipendenze
REQUIREMENTS_PATH="${PROJECT_DIR}/requirements.txt"

source "${PROJECT_DIR}/${VENV_NAME}/bin/activate"
pip install --upgrade pip

if [ -f "$REQUIREMENTS_PATH" ]; then
    echo "Installazione delle dipendenze da $REQUIREMENTS_PATH..."
    pip install -r "$REQUIREMENTS_PATH"
else
    echo "Il file $REQUIREMENTS_PATH non esiste."
fi

deactivate
