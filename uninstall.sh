#!/bin/bash

echo "Pulizia della cartella in corso..."

# Rimozione della cartella __pycache__
if [ -d "__pycache__" ]; then
    echo "Rimozione della cartella __pycache__..."
    rm -rf __pycache__
fi

# Rimozione della cartella pwb
if [ -d "pwb" ]; then
    echo "Rimozione della cartella pwb..."
    rm -rf pwb
fi

# Rimozione del file config.py
if [ -f "config.py" ]; then
    echo "Rimozione del file config.py..."
    rm -f config.py
fi

# Rimozione del file price_tables.db
if [ -f "price_tables.db" ]; then
    echo "Rimozione del file price_tables.db..."
    rm -f price_tables.db
fi

# Rimozione del file start.bat
if [ -f "start.bat" ]; then
    echo "Rimozione del file start.bat..."
    rm -f start.bat
fi

# Rimovione del file cron.log
if [ -f "cron.log" ]; then
    echo "Rimozione del file cron.log..."
    rm -f cron.log
fi

(crontab -l | grep -v 'PWB_update_prices' | crontab -) && echo "Job 'PWB_update_prices' rimosso."
(crontab -l | grep -v 'PWB_send_notify' | crontab -) && echo "Job 'PWB_send_notify' rimosso."

echo "Pulizia completata."
