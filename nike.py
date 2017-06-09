# -*- coding: utf-8 -*-

import json
import re
import requests
from bs4 import BeautifulSoup

from .crawler import Crawler


class NikeData(Crawler):
    basic_url = 'http://www.nike.co.kr/display/displayShop.lecs?stonType=P'
    basic_product_url = 'http://www.nike.co.kr/goods/showGoodsDetail.lecs?'

    category = {
        '재킷 & 베스트': 'Outer',
        '탑 & 티셔츠': 'Top',
        '브라': 'Top',
        '후디 & 크루': 'Top',
        '팬츠 & 타이츠': 'Bottom',
        '팬츠': 'Bottom',
        '전체': 'Bottom',
        '세트': 'Bottom',
        '스커트 & 드레스': 'Dress/Skirt',
        '모자 & 용품': 'Accessories',
        '악세서리 & 용품': 'Accessories',
        '신발': 'Shoes',
        '농구화': 'Shoes',
        '축구화': 'Shoes',
        '러닝화': 'Shoe'
    }

    def __init__(self):
        response = requests.get(self.basic_url)
        html = BeautifulSoup(response.text, 'lxml')

        for _ in html.find_all('a', string='가격인하'):
            sale_url = _['href']
            sale_response = requests.get(sale_url)
            sale_html = BeautifulSoup(sale_response.text, 'lxml')

            for unit in sale_html.find_all('div', class_='unit'):
                img_url = unit.find('img')['src']
                unit_url = unit.find('a')['onclick']

                # convert json to dictionary
                tmp = re.search('\{(.*)\}', unit_url).group(0)
                json_data = re.sub('(?P<p>[a-zA-Z]{7,20})', "'\g<p>'", tmp).replace("'", '"')
                dic = json.loads(json_data)

                full_unit_url = "{0}{1}".format(self.basic_product_url,
                                                'goodsNo={0}&colorOptionValueCode={1}&displayNo={2}' \
                                                .format(str(dic['goodsNo']), str(dic['colorOptionValueCode']),
                                                        str(dic['displayNo'])))

                unit_response = requests.get(full_unit_url)
                unit_html = BeautifulSoup(unit_response.text, 'lxml')

                name = unit_html.find(class_='tit').string
                original_price = unit_html.find(class_='ori_price').string.strip()

                try:
                    sale_price = unit_html.find(class_='txt_orange').string.strip()

                except AttributeError:
                    sale_price = None

                category_data = unit_html.find(class_='loc').string
                category_list = re.sub('\s+', ' ', category_data).strip()
                category_list = re.sub('[＆&]+', ' & ', category_list).split()

                while '&' in category_list:
                    index = category_list.index('&')
                    category_list[index - 1:index + 2] = [' '.join(category_list[index - 1:index + 2])]

                category = None

                for key in category_list:

                    if key in self.category:
                        category = self.category[key]

                data = {
                    'name': name,
                    'brand': 'NIKE',
                    'original price': original_price,
                    'sale price': sale_price,
                    'category': category,
                    'image url': img_url,
                    'url': full_unit_url
                }

                self.unit_list.append(data)
