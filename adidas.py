# -*- coding: utf-8 -*-

import re
import requests
from bs4 import BeautifulSoup

from .crawler import Crawler


class AdidasData(Crawler):
    basic_product_url = 'http://shop.adidas.co.kr/PF020401.action?PROD_CD='
    basic_url = 'http://shop.adidas.co.kr/PF010104.action?' \
                'command=LIST&S_CTGR_CD=01&S_LEVEL=1&S_ORDER_BY=1&S_PAGECNT=100&PAGE_CUR='

    category = {
        '자켓': 'Outer',
        '반팔티': 'Top',
        '티셔츠': 'Top',
        '긴팔티': 'Top',
        '트랙탑 / 져지탑': 'Top',
        '슬리브리스': 'Top',
        '스커트 / 원피스': 'Dress/Skirt',
        '가방': 'Bag',
        '양말': 'Accessories',
        '로우컷': 'Shoes',
        '하이컷 / 미드컷': 'Shoes'
    }

    def __init__(self):
        first_page_response = requests.get(self.basic_url)
        first_page_html = BeautifulSoup(first_page_response.text, 'lxml')
        pages = [_.string for _ in first_page_html.find('div', class_='paging_r').find_all('a')]

        for page in range(1, int(pages[-2]) + 1):
            url = self.basic_url + str(page)
            response = requests.get(url)
            html = BeautifulSoup(response.text, 'lxml')

            for product in html.find('div', class_='prodlist').find_all('li'):
                product_url_tag = product.select_one('div.img > a')

                if product_url_tag is not None:
                    op_tmp = product.find('span', class_='line_through').string
                    original_price = op_tmp[:-4] + ',' + op_tmp[-4:]

                    sp_tmp = product.select_one('span.sale em').string
                    sale_price = sp_tmp[:-3] + ',' + sp_tmp[-3:] + '원'

                    img_url = product.find('img')['src']

                    product_url = self.basic_product_url + re.search("\('(\w+)'\)", product_url_tag['href']).group(1)
                    product_response = requests.get(product_url)
                    product_html = BeautifulSoup(product_response.text, 'lxml')

                    name = product_html.find('h2', id='p_prod_bas').string

                    category_data = product_html.find('meta', property='rb:category3')['content']

                    if category_data in self.category:
                        category = self.category[category_data]

                    else:
                        category = None

                    data = {
                        'name': name,
                        'brand': 'ADIDAS',
                        'original price': original_price,
                        'sale price': sale_price,
                        'category': category,
                        'image url': img_url,
                        'url': product_url
                    }

                    self.unit_list.append(data)
