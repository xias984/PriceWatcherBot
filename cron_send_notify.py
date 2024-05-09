import requests
from database_manager import DatabaseManager
import os
import time

def main():
    DM = DatabaseManager(os.getenv('DB_HOST'),os.getenv('DB_USER'),os.getenv('DB_PASS'),os.getenv('DB_NAME'))
    with DM as db_manager:
        results = db_manager.get_recent_price_changes()
        
        for data in results:
            new_price = data[3]
            old_price = data[4]
            user_id = data[2]

            if new_price < old_price:
                word = 'diminuito'
            elif new_price > old_price:
                word = 'aumentato'

            message = f"Il prezzo di {data[0]} è {word} da {old_price} a {new_price}!"
            send_telegram_notification(user_id, message)
            time.sleep(60)

def send_telegram_notification(user_id, message):
    send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={user_id}&text={message}"
    requests.get(send_url)

if __name__ == '__main__':
    main()