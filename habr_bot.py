import telebot
from telebot import types
import habr_parser
from datetime import datetime
import queue
from common_types import User, Task, Config
    
def bot_thread(bot, config : Config, users : dict):
    @bot.message_handler(commands=['reg'])
    def reg_handler(message):
        if (message.from_user.id not in users):
            users[message.from_user.id] = User(message.from_user.id, [])
            bot.send_message(message.from_user.id, "Registered new user", parse_mode='Markdown')

    @bot.message_handler(commands=['keys'])
    def keys_handler(message):
        reg_handler(message)
        keys = message.text.replace('/keys ', '')
        for key in keys.split(' '):
            users[message.from_user.id].filters.append(key)
            print(key)

    bot.polling(none_stop=True, interval=0)

def notifier_thread(bot, users : dict, tasks_queue : queue.Queue):

    characters_to_replace = [".", "-", "!", "*", "'", "(", ")", ";", ":", "@", "&", "=", "+", "$", ",", "/", "?", "%", "#", "[", "]"]

    while(True):
        new_tasks = []

        while not tasks_queue.empty():
            new_tasks.append(tasks_queue.get())

        if len(new_tasks) == 0:
            continue

        if len(users) == 0:
            continue

        for task in new_tasks:
            temp_list = []
            for user in users.values():
                
                if (len(user.filters) == 0):
                    temp_list = new_tasks
                    break
                for filter in user.filters:
                    if filter in task.title or filter in ' '.join(task.tags):
                        temp_list.append(task)
                        break
            for temp_task in temp_list:
                t = temp_task.title
                for c in characters_to_replace:
                    t = t.replace(c, f'\{c}')
                bot.send_message(user.id, f'[{t}]({temp_task.url.strip()})', parse_mode='MarkdownV2', disable_web_page_preview=True)

