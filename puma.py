# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

from .crawler import Crawler


class PumaData(Crawler):
    basic_url = 'https://kr.puma.com/aramenu/ajax/productview/?'

    category_dict = {
        '116': 'Shoes',
        '117': 'Top',
        '118': 'Accessories'
    }

    def __init__(self):

        for category in self.category_dict:
            category_url = self.basic_url + 'category=' + category
            response = requests.get(category_url)
            html = BeautifulSoup(response.text, 'lxml')

            last_page = int(html.find('a', title='Last')['href'].split('=')[-1])

            for page in range(1, last_page + 1):
                page_url = category_url + '&p=' + str(page)
                page_response = requests.get(page_url)
                page_html = BeautifulSoup(page_response.text, 'lxml')

                for product in page_html.find_all('li', class_='item'):
                    url = product.find('a', class_='product-image')['href']
                    img_url = product.find('img')['src'].replace('//', 'https://')
                    name = product.select_one('h2.product-name a').string
                    original_price = product.find('span', class_='puma_price_line').string
                    sale_price = product.find('span', class_='puma_red_p').string

                    data = {
                        'name': name,
                        'brand': 'PUMA',
                        'original price': original_price,
                        'sale price': sale_price,
                        'category': self.category_dict[category],
                        'image url': img_url,
                        'url': url
                    }

                    self.unit_list.append(data)
