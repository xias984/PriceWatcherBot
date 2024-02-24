#!/bin/bash

# Percorso del database
DATABASE_PATH="price_tables.db"

# Percorso del file SQL
SQL_FILE_PATH="price_tables.sql"

# Backup del database (opzionale)
echo "Creazione del backup del database..."
cp "$DATABASE_PATH" "${DATABASE_PATH}.backup"

# Cancellazione del database esistente
echo "Cancellazione del database esistente..."
rm -f "$DATABASE_PATH"

# Verifica che il file SQL esista
if [ ! -f "$SQL_FILE_PATH" ]; then
    echo "Il file SQL $SQL_FILE_PATH non esiste."
    exit 1
fi

# Ricreazione del database e importazione della struttura e dei dati
echo "Ricreazione del database e importazione della struttura e dei dati..."
sqlite3 "$DATABASE_PATH" < "$SQL_FILE_PATH"

echo "Operazione completata con successo."