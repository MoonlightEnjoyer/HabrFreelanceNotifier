from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import psycopg2
from psycopg2 import Error
from psycopg2 import sql
import datetime
import queue
from common_types import Config, User, Task
import database_operations

def replace_month_name(month_str) -> str:
    return month_str.replace('января', '01').replace('февраля', '02').replace('марта', '03').replace('апреля', '04').replace('мая', '05').replace('июня', '06').replace('июля', '07').replace('августа', '08').replace('сентября', '09').replace('октября', '10').replace('ноября', '11').replace('декабря', '12')

def fill_tasks_table(config : Config):
    url = f'https://freelance.habr.com/tasks?page='
    tasks = []
    ua = UserAgent()

    headers = {
        'accept': 'application/json, text/plain, */*',
        'user-Agent': ua.google,
    }

    page = 1

    try:
        connection = psycopg2.connect(user=config.database_user, password=config.password, host=config.host, port=config.port, database=config.database)
        cursor = connection.cursor()

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

            description = soup.find('div', class_='task__description').text.strip().replace('\n', ' ')
            pub_time =  replace_month_name(soup.find('div', class_='task__meta').next.replace('•', ' ').strip().replace('\n', ' ').replace(',', '')).split(' ')
            pub_time = f'{pub_time[2]}-{pub_time[1]}-{pub_time[0]} {pub_time[3]}:00'
                
            tags = []

            for raw_tag in raw_tags:
                tags.append(raw_tag.string)

            database_operations.insert_task(cursor=cursor, connection=connection, title=title, tags=tags, description=description, ref=ref, pub_time=pub_time)


            print(f'{progress} / {len(tasks)}')

            progress += 1

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

def get_new_tasks(config : Config, tasks_queue : queue.Queue):
    url = f'https://freelance.habr.com/tasks?page='
    tasks = []
    ua = UserAgent()

    headers = {
        'accept': 'application/json, text/plain, */*',
        'user-Agent': ua.google,
    }

    page = 1

    try:
        connection = psycopg2.connect(user=config.database_user, password=config.password, host=config.host, port=config.port, database=config.database)

        cursor = connection.cursor()

        cursor.execute(sql.SQL("SELECT MAX (PUBLISH_TIME) FROM TASKS"))
        connection.commit()

        last_inserted_task = cursor.fetchall()[0][0]

        res = requests.get(url + str(page), headers=headers)

        res.close()
        req = res.text

        soup = BeautifulSoup(req, 'lxml')

        raw_tasks = soup.find_all('div', class_='task__title')

        for raw_task in raw_tasks:
            tasks.append(raw_task)

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

            description = soup.find('div', class_='task__description').text.strip().replace('\n', ' ')
            pub_time =  replace_month_name(soup.find('div', class_='task__meta').next.replace('•', ' ').strip().replace('\n', ' ').replace(',', '')).split(' ')
            pub_time = f'{pub_time[2]}-{pub_time[1]}-{pub_time[0]} {pub_time[3]}:00'
            pub_time_datetime = datetime.datetime.strptime(pub_time, '%Y-%m-%d %H:%M:%S')
            
            if (last_inserted_task >= pub_time_datetime):
                continue
                
            tags = []

            for raw_tag in raw_tags:
                tags.append(raw_tag.string)

            database_operations.insert_task(cursor=cursor, connection=connection, title=title, tags=tags, description=description, ref=ref, pub_time=pub_time)

            tasks_queue.put(Task(title, tags, description, f'https://freelance.habr.com{ref}', pub_time_datetime))

            print(f'{progress} / {len(tasks)}')

            progress += 1
        
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
    
def select_tasks(config : Config, filters) -> list[Task]:    
    try:
        connection = psycopg2.connect(user=config.database_user, password=config.password, host=config.host, port=config.port, database=config.database)

        cursor = connection.cursor()

        if len(filters) == 0:
            cursor.execute(sql.SQL("SELECT * FROM TASKS"))
            connection.commit()
        else:
            for filter in filters:
                cursor.execute(sql.SQL(f"SELECT * FROM TASKS WHERE ('{filter}' = ANY(TAGS)) OR (DESCRIPTION like '%{filter}%') OR (TITLE like '%{filter}%')"))
            connection.commit()

        records = cursor.fetchall()

        tasks = []
        
        for record in records:
            tasks.append(Task(record[1], record[2], record[3], record[4], record[5]))

        return tasks

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()