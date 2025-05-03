import requests
from bs4 import BeautifulSoup
import random
from config import logger
import re

class AmazonScraper:
    def __init__(self):
        self.userAgents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
        ]
        self.logger = logger

    def fetch_amazon_data(self, url):
        headers = {'User-Agent': random.choice(self.userAgents)}
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            price = self.get_price(soup)
            category = self.get_category(soup)
            asin = self.get_asin(soup)
            productName = self.get_product_name(soup)
            return [price, productName, asin, category, url]
        except Exception as e:
            self.logger.error(f"Errore durante il fetch del prezzo: {e}")
            return None

    def get_price(self, soup):
        try:
            # 1. Prova con gli input ID noti
            list_input_id = ['priceValue', 'twister-plus-price-data-price']
            for input_id in list_input_id:
                price = soup.find('input', id=input_id)
                if price and 'value' in price.attrs:
                    return self.clean_price(price['value'])

            # 2. Prova con ID classico Amazon (fallback legacy)
            price_span = soup.find('span', id='priceblock_ourprice')
            if price_span:
                return self.clean_price(price_span.text)

            # 3. Prova a costruire prezzo da a-price-whole + a-price-fraction
            price_container = soup.find('span', class_='a-price')
            if price_container:
                whole = price_container.find('span', class_='a-price-whole')
                fraction = price_container.find('span', class_='a-price-fraction')
                if whole and fraction:
                    return self.clean_price(f"{whole.text.strip()}.{fraction.text.strip()}")

            # Nessun prezzo trovato
            self.logger.info("Nessun prezzo trovato")
            return 'Prezzo non trovato'

        except Exception as e:
            self.logger.error(f"Errore durante l'estrazione del prezzo: {e}")
            return 'Prezzo non trovato'

    def clean_price(self, raw_price):
        """
        Pulisce il prezzo, estraendo numeri e punto decimale.
        """
        clean = raw_price.replace('€', '').replace(',', '.').strip()
        # Rimuove tutto ciò che non è cifra o punto
        clean = re.sub(r'[^\d.]', '', clean)
        # Se ci sono più punti, prende solo il primo come decimale
        parts = clean.split('.')
        if len(parts) > 2:
            clean = f"{parts[0]}.{''.join(parts[1:])}"
        return clean

    def get_category(self, soup):
        first_span = soup.find('ul', class_="a-unordered-list a-horizontal a-size-small")
        if first_span:
            category_link = first_span.find('li').find('span').find('a')
            if category_link:
                category = category_link.text.strip()
                return category
        return 'Non trovata'


    def get_asin(self, soup):
        asin = soup.find('input', {'id': 'ASIN'})
        if asin:
            return asin['value']
        return 'Non disponibile'

    def get_product_name(self, soup):
        productName = soup.find('span', {'id': 'productTitle'})
        if productName:
            return productName.text.strip()
        return 'Non disponibile'

