from bs4 import BeautifulSoup
import random
import json
import requests
import datetime
from fake_useragent import UserAgent
import re
import telebot
from telebot import types
import threading

users = []

token = ''

with open('../teletoken.txt', 'r') as token_file:
    token = token_file.readline()
    token = token.strip()

bot = telebot.TeleBot(token)

class Task:
    title = str()
    tags = list[str]
    url = str()

    def __eq__(self, __value: object) -> bool:
        return self.title == object.title and self.tags == object.tags
    
def create_tasks_database():
    url = f'https://freelance.habr.com/tasks?page='
    tasks = []
    ua = UserAgent()

    headers = {
        'accept': 'application/json, text/plain, */*',
        'user-Agent': ua.google,
    }


    page = 1

    with open('./tasks.txt', 'w') as database:
        while (True):

            try:
                res = requests.get(url + str(page), headers=headers)
            except:
                continue
            
            res.close()
            req = res.text

            soup = BeautifulSoup(req, 'lxml')

            raw_tasks = soup.find_all('div', class_='task__title')

            if len(raw_tasks) == 0:
                break



            for raw_task in raw_tasks:
                tasks.append(raw_task)

            page += 1

        progress = 0
        for task in tasks:
            ref = str(task.find('a').get('href'))
            res = requests.get(f'https://freelance.habr.com{ref}')
            res.close()
            if res.status_code != 200:
                continue
            req = res.text
            soup = BeautifulSoup(req, 'lxml')
            title = soup.find('h2' ,class_='task__title').text.strip().replace('\n', ' ')
            raw_tags = soup.find_all('a', class_='tags__item_link')
                
            tags = []

            for raw_tag in raw_tags:
                tags.append(raw_tag.string)

            database.write(f'{title}; {",".join(tags)}; https://freelance.habr.com{ref}\n')
            database.flush()

            print(f'{progress} / {len(tasks)}')

            progress += 1

def read_tasks_database() -> list[Task]:
    result = []
    with open('tasks.txt', 'r') as database:
        while True:
            line = database.readline()
            if not line:
                break
            raw_task = line.split(';')
            task = Task()
            task.title = raw_task[0]
            task.tags = raw_task[1].split(',')
            task.url = raw_task[2]
            result.append(task)

    return result



def bot_thread():
    @bot.message_handler(commands=['start'])
    def start(message):
        print("before user append")
        if (users.count(message.from_user.id) == 0):
            users.append(message.from_user.id)
            print("Appended user")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(message.from_user.id, "Looking for tasks...", reply_markup=markup)



    bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть

def parser_thread():

    list_of_jobs = []
    ua = UserAgent()

    headers = {
        'accept': 'application/json, text/plain, */*',
        'user-Agent': ua.google,
    }

    article_dict = {}


    url = f'https://freelance.habr.com/tasks?page='
    

    filters = ['python']

    #create_tasks_database()

    tasks_database = read_tasks_database()

    characters_ta_replace = [".", "-", "!", "*", "'", "(", ")", ";", ":", "@", "&", "=", "+", "$", ",", "/", "?", "%", "#", "[", "]"]

    while(True):
        if (len(users) == 0):
            continue


        temp_list = []
        for task in tasks_database:
            for filter in filters:
                if filter in task.title or filter in ' '.join(task.tags):
                    t = task.title
                    for c in characters_ta_replace:
                        t = t.replace(c, f'\{c}')
                    temp_list.append(f'[{t}]({task.url.strip()})')
                    

        if (list_of_jobs != temp_list):
            list_of_jobs = temp_list
            for elem in list_of_jobs:
                bot.send_message(users[0], elem, parse_mode='MarkdownV2', disable_web_page_preview=True)

b_t = threading.Thread(target=bot_thread)
p_t = threading.Thread(target=parser_thread)


b_t.start()
p_t.start()

