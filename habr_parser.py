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

    #page = 1

    res = requests.get(url, headers=headers)
    res.close()
    req = res.text

    soup = BeautifulSoup(req, 'lxml')

    raw_tasks = soup.find_all('div', class_='task__title')

    for raw_task in raw_tasks:
        tasks.append(raw_task)

    progress = 0

    characters_to_replace = [".", "-", "!", "*", "'", "(", ")", ";", ":", "@", "&", "=", "+", "$", ",", "/", "?", "%", "#", "[", "]"]

    for task in reversed(tasks):

        print(f'{progress} / {len(tasks)}')
        progress += 1

        ref = str(task.find('a').get('href'))
        res = requests.get(f'https://freelance.habr.com{ref}')
        res.close()
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
        
        if (common_types.last_inserted_task >= pub_time_datetime):
            continue
        
        common_types.last_inserted_task = pub_time_datetime

        tags = []

        for raw_tag in raw_tags:
            tags.append(raw_tag.string)

        t = title
        for c in characters_to_replace:
            t = t.replace(c, f'\{c}')
        tasks_queue.put(Task('habr', f'[{t}]({url.strip()})'))
