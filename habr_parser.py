from bs4 import BeautifulSoup
import random
import json
import requests
import datetime
from fake_useragent import UserAgent
import re
import telebot

# ua = UserAgent()

# headers = {
#     'accept': 'application/json, text/plain, */*',
#     'user-Agent': ua.google,
# }

# article_dict = {}


# url = f'https://freelance.habr.com/tasks/'

# res = requests.get(url, headers=headers)
# res.close()
# req = res.text

# soup = BeautifulSoup(req, 'lxml')
# categories = soup.find_all('div', class_='task__title')

# for category in categories:
#     # print(f'https://companies.rbc.ru{category.get("href")}')
#     print(category.get('title'))
#     #subcategories = soup.find_all('a', class_='block mb-[12px] text-[15px] font-medium leading-[1.6]')

