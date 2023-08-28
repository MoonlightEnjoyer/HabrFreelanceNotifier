from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import datetime
import queue
from common_types import Config, User, Task
import common_types

def replace_month_name(month_str) -> str:
    return month_str.replace('января', '01').replace('февраля', '02').replace('марта', '03').replace('апреля', '04').replace('мая', '05').replace('июня', '06').replace('июля', '07').replace('августа', '08').replace('сентября', '09').replace('октября', '10').replace('ноября', '11').replace('декабря', '12')

#pushes task objects to the common queue
def get_new_tasks(config : Config, tasks_queue : queue.Queue):
    url = f'https://freelance.habr.com/tasks'
    tasks = []
    ua = UserAgent()

    headers = {
        'accept': 'application/json, text/plain, */*',
        'user-Agent': ua.google,
    }

    for i in range(5):
        try:
            res = requests.get(url, headers=headers)
            res.close()
            break
        except:
            print("Connection failed.")
            return

    req = res.text

    soup = BeautifulSoup(req, 'lxml')

    raw_tasks = soup.find_all('div', class_='task__title')

    for raw_task in raw_tasks:
        tasks.append(raw_task)

    progress = 0

    characters_to_replace = [".", "-", "!", "*", "'", "(", ")", ";", ":", "@", "&", "=", "+", "$", ",", "/", "?", "%", "#", "[", "]", '|']

    for task in reversed(tasks):

        print(f'{progress} / {len(tasks)}')
        progress += 1

        if hash(task.string) in common_types.last_task_hashes:
            print('skip')
            continue

        ref = str(task.find('a').get('href'))
        for i in range(5):
            try:
                res = requests.get(f'https://freelance.habr.com{ref}')
                res.close()
                break
            except:
                pass

        if res.status_code != 200:
            continue
        req = res.text
        soup = BeautifulSoup(req, 'lxml')
        title = soup.find('h2' ,class_='task__title').text.strip().replace('\n', ' ')
        raw_tags = soup.find_all('a', class_='tags__item_link')

        description = soup.find('div', class_='task__description').text.strip().replace('\n', ' ')
        pub_time =  replace_month_name(soup.find('div', class_='task__meta').next.replace('•', ' ').strip().replace('\n', ' ').replace(',', '')).split(' ')
        pub_time = f'{pub_time[2]}-{pub_time[1]}-{pub_time[0]} {pub_time[3]}:00'
        pub_time_datetime = datetime.datetime.strptime(pub_time, '%Y-%m-%d %H:%M:%S')
        
        common_types.last_task_hashes.append(hash(task.string))

        if (common_types.last_inserted_task >= pub_time_datetime):
            continue
        
        common_types.last_inserted_task = pub_time_datetime
        
        if len(common_types.last_task_hashes) > 25:
            common_types.last_task_hashes = common_types.last_task_hashes[-25:]

        search_payload = []

        for raw_tag in raw_tags:
            search_payload.append(raw_tag.string)

        escaped_title = title
        escaped_description = description
        for c in characters_to_replace:
            escaped_title = escaped_title.replace(c, f'\{c}')
            escaped_description = escaped_description.replace(c, ' ')

        description_splitted = description.strip().split(' ')

        for description_part in description_splitted:
            search_payload.append(description_part)

        title_splitted = title.split(' ')

        for title_part in title_splitted:
            search_payload.append(title_part)


        tasks_queue.put(Task('habr', f'[{escaped_title}](https://freelance.habr.com{ref.strip()})', search_payload))
