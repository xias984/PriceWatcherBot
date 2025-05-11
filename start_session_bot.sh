#!/bin/bash

# Copia il file sessione nella root
if [ ! -f /app/PriceWatcherBot.session ]; then
    cp /app/session_listener/PriceWatcherBot.session /app/
fi
cd "$(dirname "$0")" 
# Avvia lo script Python
exec python -m session_listener.session_bot
