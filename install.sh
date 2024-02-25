#!/bin/bash

# Definisci il nome e il percorso dell'ambiente virtuale
VENV_NAME="bot"
PROJECT_DIR=$(pwd)
VENV_PATH="$PROJECT_DIR/$VENV_NAME"
VENV_SCRIPTS_PATH="$VENV_PATH/bin"

# Crea l'ambiente virtuale
python3 -m venv "$VENV_NAME"
echo "Ambiente virtuale $VENV_NAME creato con successo."

# Aggiorna pip e installa le dipendenze
source "$VENV_SCRIPTS_PATH/activate"
pip install --upgrade pip

REQUIREMENTS_PATH="$PROJECT_DIR/requirements.txt"
if [ -f "$REQUIREMENTS_PATH" ]; then
    echo "Installazione delle dipendenze da $REQUIREMENTS_PATH..."
    pip install -r "$REQUIREMENTS_PATH"
else
    echo "Il file $REQUIREMENTS_PATH non esiste."
fi

# Modifica il file amazonify.py nell'ambiente virtuale, se necessario
FILE_PATH="$VENV_PATH/lib/python3.X/site-packages/amazonify.py" # Sostituisci python3.X con la tua versione specifica di Python

if [ -f "$FILE_PATH" ]; then
    echo "Modifica in corso di $FILE_PATH..."
    sed -i "s/from urlparse import urlparse, urlunparse/from urllib.parse import urlparse, urlunparse/g" "$FILE_PATH"
    echo "Sostituzione effettuata con successo."
else
    echo "Il file specificato non esiste: $FILE_PATH"
fi

# Configura il job cron
CRON_JOB="0 5 * * * cd $PROJECT_DIR && $VENV_SCRIPTS_PATH/python cron_update_prices.py >> cron.log 2>&1"

# Aggiunge il job cron se non esiste
(crontab -l 2>/dev/null | grep -Fv cron_update_prices; echo "$CRON_JOB") | crontab -

echo "Job cron per l'aggiornamento dei prezzi configurato con successo."

# Crea il database, se non esiste
DATABASE_PATH="price_tables.db"
SQL_FILE_PATH="price_tables.sql"

if [ -f "$DATABASE_PATH" ]; then
    echo "Il file del database esiste già."
else
    echo "Creazione del database da $SQL_FILE_PATH..."
    sqlite3 "$DATABASE_PATH" < "$SQL_FILE_PATH"
    echo "Database creato."
fi

# Crea start.sh con il comando desiderato
echo "#!/bin/bash
echo \"Esecuzione PriceWatcherBot in corso...\"
\"$VENV_SCRIPTS_PATH/python\" main.py
echo
echo \"Premere CTRL+C per uscire...\"
read -n 1 -s -r -p \"Press any key to continue\"
" > start.sh
chmod +x start.sh

# Configura le variabili di configurazione
echo "Configurazione di config_sample.py..."
cp config_sample.py config.py

read -p "Inserisci il token del bot Telegram: " TELEGRAM_TOKEN
read -p "Inserisci l'affiliate tag di Amazon: " AMAZON_AFFILIATE_TAG

sed -i "s/your_database_name_here/$DATABASE_PATH/g" config.py
sed -i "s/your_telegram_token_here/$TELEGRAM_TOKEN/g" config.py
sed -i "s/your_amazon_affiliate_tag_here/$AMAZON_AFFILIATE_TAG/g" config.py

echo "Configurazione completata."
