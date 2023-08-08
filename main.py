import habr_parser
import habr_bot
import threading
import time
import queue


def get_new_tasks_thread(tasks_queue):
    while(True):
        habr_parser.get_new_tasks(tasks_queue)
        time.sleep(60)


tasks_queue = queue.Queue()

filters = []

b_t = threading.Thread(target=habr_bot.bot_thread, args=(filters,))
p_t = threading.Thread(target=habr_bot.notifier_thread, args=(filters, tasks_queue))

b_t.start()
p_t.start()

        

gt_t = threading.Thread(target=get_new_tasks_thread, args=(tasks_queue,))
gt_t.start()


# habr_parser.createTasksTable()
# habr_parser.fill_tasks_table()

# tasks = habr_parser.select_tasks(['python'])
# for task in tasks:
#     print(f'{task.title}, {task.tags}, {task.url}')