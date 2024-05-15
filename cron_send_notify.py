import requests
from database_manager import DatabaseManager
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME, TELEGRAM_BOT_TOKEN, logger
from urllib.parse import urlencode
import time

def main():
    DM = DatabaseManager(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    with DM as db_manager:
        results = db_manager.get_recent_price_changes()
        
        for data in results:
            logger.info(data[2])
            new_price = data[3]
            old_price = data[4]
            user_id = data[2]

            if new_price < old_price:
                word = 'diminuito'
            elif new_price > old_price:
                word = 'aumentato'

            message = f"Il prezzo di {data[0]} è {word} da {old_price} a {new_price}!"
            params = {
                'chat_id': user_id,
                'text': message
            }
            if params[0] and params[1]:
                send_telegram_notification(params)

def send_telegram_notification(params):
    base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    send_url = f"{base_url}?{urlencode(params)}"
    try:
        response = requests.get(send_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logger.error(f"Errore HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logger.error(f"Errore di connessione: {errc}")
    except requests.exceptions.Timeout as errt:
        logger.error(f"Timeout: {errt}")
    except requests.exceptions.RequestException as err:
        logger.error(f"Errore nella richiesta: {err}")

if __name__ == '__main__':
    main()