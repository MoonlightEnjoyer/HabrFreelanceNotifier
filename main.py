import habr_parser
import habr_bot
import threading
import time
import queue
from common_types import Config
import telebot

def get_new_tasks_thread(config, tasks_queue):
    while(True):
        habr_parser.get_new_tasks(config, tasks_queue)
        time.sleep(60)

tasks_queue = queue.Queue()

users = {}

config = Config()

bot = telebot.TeleBot(config.token)

bot_thread = threading.Thread(target=habr_bot.bot_thread, args=(bot, config, users, ))
notifyer_thread = threading.Thread(target=habr_bot.notifier_thread, args=(bot, users, tasks_queue))
parser_thread = threading.Thread(target=get_new_tasks_thread, args=(config, tasks_queue,))

bot_thread.start()
notifyer_thread.start()
parser_thread.start()