import requests
from bs4 import BeautifulSoup
import random
from amazonify import amazonify
from config import AMAZON_AFFILIATE_TAG

class AmazonScraper:
    def __init__(self, affiliate_tag=AMAZON_AFFILIATE_TAG):
        self.affiliate = affiliate_tag
        self.userAgents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
        ]

    def amz_link_building(self, url):
        return amazonify(url, self.affiliate)

    def fetch_amazon_data(self, url):# -> list[Any | str] | None:
        url = self.amz_link_building(url)
        headers = {'User-Agent': random.choice(self.userAgents)}
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            price = self.get_price(soup)
            category = self.get_category(soup)
            asin = self.get_asin(soup)
            productName = self.get_product_name(soup)
            return [price, productName, asin, category]
        except Exception as e:
            print(f"Errore durante il fetch del prezzo: {e}")
            return None

    def get_price(self, soup):
        list_input_id = ['priceValue', 'twister-plus-price-data-price']
        for input_id in list_input_id:
            price = soup.find('input', id=input_id)
            if price:
                return price['value']
        # Se non trova il prezzo nei campi input, cerca in altre possibili posizioni
        price_span = soup.find('span', id='priceblock_ourprice')
        if price_span:
            return price_span.text.strip()
        return 'Non disponibile'

    def get_category(self, soup):
        try:
            first_span = soup.find('ul', class_="a-unordered-list a-horizontal a-size-small").find('li').find('span')
            category = first_span.find('a').text.strip()
            return category
        except TypeError:
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

