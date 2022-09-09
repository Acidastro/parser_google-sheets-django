"""
Парсим курс валюты по API ЦБ РФ на сегодняшний день
"""

from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs


def currency_parsing():
    d = datetime.now().strftime('%d')
    m = datetime.now().strftime('%m')
    y = datetime.now().strftime('%Y')

    # Делаем запрос на сайт, передаем ему параметр.
    url = 'http://www.cbr.ru/scripts/XML_daily.asp?'
    params = {
        'date_req': '{0}/{1}/{2}'.format(d, m, y)
    }

    request = requests.get(url, params)
    soup = bs(request.content, 'xml')
    find_usd = soup.find(ID='R01235').Value.string
    res = float(find_usd[:2]) + float(find_usd[3:]) / 10000
    return res


if __name__ == '__main__':
    currency_parsing()
