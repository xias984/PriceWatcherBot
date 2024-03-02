import requests
from bs4 import BeautifulSoup
import random

class AmazonScraper:
    def __init__(self):
        self.userAgents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
        ]

    def fetch_amazon_data(self, url):
        headers = {'User-Agent': random.choice(self.userAgents)}
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            price = self.get_price(soup)
            category = self.get_category(soup)
            asin = self.get_asin(soup)
            productName = self.get_product_name(soup)
            return [price, productName, asin, category, urlBuilded]
        except Exception as e:
            print(f"Errore durante il fetch del prezzo: {e}")
            return None

    def get_price(self, soup):
        list_input_id = ['priceValue', 'twister-plus-price-data-price']
        for input_id in list_input_id:
            price = soup.find('input', id=input_id)
            if price and 'value' in price.attrs:
                return price['value'].strip()
        price_span = soup.find('span', id='priceblock_ourprice')
        if price_span:
            return price_span.text.strip()
        return 'Non disponibile'


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

