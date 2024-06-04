from database_manager import DatabaseManager
from amazon_scraper import AmazonScraper
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME, logger_cron
import time

def main():
    AS = AmazonScraper()
    DM = DatabaseManager(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    with DM as db_manager:
        results = db_manager.get_price_for_scraping()
        for data in results:
            AmazonPrice = AS.fetch_amazon_data(data[2])[0]
            if AmazonPrice == 'Non disponibile':
                AmazonPrice = 0
            if float(AmazonPrice) and (float(AmazonPrice) != float(data[1])):
                db_manager.update_variation_price(data[0], data[1], AmazonPrice)
                logger_cron.info(f'Prodotto {data[0]} aggiornato')
            logger_cron.info(f"Prodotto {data[0]} analizzato. Prezzo {AmazonPrice}")
            time.sleep(60)
            

if __name__ == '__main__':
    logger_cron.info(f"Inizio update prezzi")
    main()
    logger_cron.info(f"Fine update prezzi")
