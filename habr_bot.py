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

    # @bot.message_handler(commands=['keys'])
    # def keys_handler(message):
    #     reg_handler(message)
    #     keys = message.text.replace('/keys ', '')
    #     for key in keys.split(' '):
    #         users[message.from_user.id].filters.append(key)
    #         print(key)

    while True:
        try:
            bot.polling(none_stop = True, interval = 0)
        except Exception:
            pass

def notifier_thread(bot, users : dict, tasks_queue : queue.Queue):
    while(True):
        new_tasks = []

        while not tasks_queue.empty():
            new_tasks.append(tasks_queue.get())

        if len(new_tasks) == 0:
            continue

        if len(users) == 0:
            continue

        for user in users.values():
            for temp_task in new_tasks:
                bot.send_message(user.id, temp_task.message, parse_mode='MarkdownV2', disable_web_page_preview=True)
