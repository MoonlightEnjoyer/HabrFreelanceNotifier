import habr_parser
import habr_bot

#filters = []
# b_t = threading.Thread(target=bot_thread, args=(filters,))
# p_t = threading.Thread(target=parser_thread, args=(filters,))

# b_t.start()
# p_t.start()


# habr_parser.createTasksTable()
# habr_parser.fill_tasks_table()

tasks = habr_parser.select_tasks(['python'])
for task in tasks:
    print(f'{task.title}, {task.tags}, {task.url}')