from bs4 import BeautifulSoup
import random
import json
import requests
import datetime
from fake_useragent import UserAgent
import re
import telebot
from telebot import types

token = ''

with open('../teletoken.txt', 'r') as token_file:
    token = token_file.readline()

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 Привет! Я твой бот-помошник!", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == '👋 Поздороваться':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton('Как стать автором на Хабре?')
        btn2 = types.KeyboardButton('Правила сайта')
        btn3 = types.KeyboardButton('Советы по оформлению публикации')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, '❓ Задайте интересующий вас вопрос', reply_markup=markup) #ответ бота


    elif message.text == 'Как стать автором на Хабре?':
        bot.send_message(message.from_user.id, 'Вы пишете первый пост, его проверяют модераторы, и, если всё хорошо, отправляют в основную ленту Хабра, где он набирает просмотры, комментарии и рейтинг. В дальнейшем премодерация уже не понадобится. Если с постом что-то не так, вас попросят его доработать.\n \nПолный текст можно прочитать по ' + '[ссылке](https://habr.com/ru/sandbox/start/)', parse_mode='Markdown')

    elif message.text == 'Правила сайта':
        bot.send_message(message.from_user.id, 'Прочитать правила сайта вы можете по ' + '[ссылке](https://habr.com/ru/docs/help/rules/)', parse_mode='Markdown')

    elif message.text == 'Советы по оформлению публикации':
        bot.send_message(message.from_user.id, 'Подробно про советы по оформлению публикаций прочитать по ' + '[ссылке](https://habr.com/ru/docs/companies/design/)', parse_mode='Markdown')




bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть



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

