from database_manager import DatabaseManager
from amazon_scraper import AmazonScraper
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME, logger
import time

def main():
    AS = AmazonScraper()
    DM = DatabaseManager(DB_HOST, DB_USER, DB_PASS, DB_NAME)
    with DM as db_manager:
        results = db_manager.get_price_for_scraping()
        for data in results:
            AmazonPrice = AS.fetch_amazon_data(data[2])[0]
            if float(AmazonPrice) and (float(AmazonPrice) != float(data[1])):
                DM.update_variation_price(data[0], data[1], AmazonPrice)
                logger.info(f'Prodotto {data[0]} aggiornato')
                time.sleep(60)
            

if __name__ == '__main__':
    main()
