# PriceWatcherBot
## INSTALLAZIONE

1. Creare un virtual environment da terminale
- Windows: `python -m venv nome_env`
- Linux: `python3 -m venv nome_env`

2. Attivare virtual environment
- Windows: `.\nome_env\Script\activate`
- Linux: `source nome_env/bin/activate`

3. Creare il database
- Windows: Eseguire `makedb.bat`
- Linux: Impostare i permessi di `makedb.sh` con `chmod +x makedb.sh` ed eseguirlo con `.\makedb.sh`

4. Installare le dipendenze
Assicurarsi che la versione di Python sia la 3.12.2 e pip con la versione 24.0 ed eseguire comando da terminale: `pip install -r requirements.txt`

5. Correggere nome modulo su `nome_env\Lib\site-packages\amazonify.py` su riga 4 da `from urlparse import urlparse, urlunparse` a `from urllib.parse import urlparse, urlunparse`