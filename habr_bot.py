import telebot
from telebot import types
import habr_parser
from datetime import datetime
import queue

users = []

token = ''

with open('../config.txt', 'r') as token_file:
    lines = token_file.readlines()
    token = lines[0].strip()
    db_password = lines[1].strip()

bot = telebot.TeleBot(token)
    
def bot_thread(filters):

    @bot.message_handler(commands=['start'])
    def start(message):
        pass

    @bot.message_handler(commands=['search'])
    def start(message):
        if (users.count(message.from_user.id) == 0):
            users.append(message.from_user.id)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(message.from_user.id, "Looking for tasks...", reply_markup=markup)

    @bot.message_handler(commands=['keys'])
    def start(message):
        keys = message.text.replace('/keys ', '')
        for key in keys.split(' '):
            filters.append(key)
            print(key)

    bot.polling(none_stop=True, interval=0)

def notifier_thread(filters : list[str], tasks_queue : queue.Queue):

    list_of_jobs = []

    characters_to_replace = [".", "-", "!", "*", "'", "(", ")", ";", ":", "@", "&", "=", "+", "$", ",", "/", "?", "%", "#", "[", "]"]

    while(True):
        new_tasks = []

        while not tasks_queue.empty():
            new_tasks.append(tasks_queue.get())

        if len(new_tasks) == 0:
            continue

        if len(users) == 0:
            continue

        temp_list = []
        for task in new_tasks:
            if (len(filters) == 0):
                temp_list = new_tasks
                break
            for filter in filters:
                if filter in task.title or filter in ' '.join(task.tags):
                    t = task.title
                    for c in characters_to_replace:
                        t = t.replace(c, f'\{c}')
                    temp_list.append(f'[{t}]({task.url.strip()})')

        for elem in temp_list:
            bot.send_message(users[0], elem, parse_mode='MarkdownV2', disable_web_page_preview=True)

        # temp_list = []
        # for task in tasks_database:
        #     for filter in filters:
        #         if filter in task.title or filter in ' '.join(task.tags):
        #             t = task.title
        #             for c in characters_to_replace:
        #                 t = t.replace(c, f'\{c}')
        #             temp_list.append(f'[{t}]({task.url.strip()})')
                    
        # if (list_of_jobs != temp_list):
        #     list_of_jobs = temp_list
        #     for elem in list_of_jobs:
        #         bot.send_message(users[0], elem, parse_mode='MarkdownV2', disable_web_page_preview=True)
