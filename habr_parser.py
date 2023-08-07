from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import psycopg2
from psycopg2 import Error
from psycopg2 import sql

password = ''

with open('../config.txt', 'r') as token_file:
    lines = token_file.readlines()
    token = lines[0].strip()
    password = lines[1].strip()


class Task:
    def __init__(self, title, tags, description, url) -> None:
        self.title = title
        self.tags = tags
        self.description = description
        self.url = url

    def __eq__(self, __value: object) -> bool:
        return self.title == object.title
    

def createTasksTable():
    try:
        connection = psycopg2.connect(user="dude",
                                      password=password,
                                      host="localhost",
                                      port="5432",
                                      database="tasks")

        cursor = connection.cursor()

        cursor.execute(sql.SQL(
            "CREATE TABLE IF NOT EXISTS TASKS (ID INT PRIMARY KEY NOT NULL, TITLE VARCHAR NOT NULL, TAGS VARCHAR ARRAY, URL VARCHAR)"))
        connection.commit()

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

def fill_tasks_table():
    url = f'https://freelance.habr.com/tasks?page='
    tasks = []
    ua = UserAgent()

    headers = {
        'accept': 'application/json, text/plain, */*',
        'user-Agent': ua.google,
    }


    page = 1

    try:
        connection = psycopg2.connect(user="dude",
                                      password=password,
                                      host="localhost",
                                      port="5432",
                                      database="tasks")

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

            description = soup.find('div', class_='task__description')
                
            tags = []

            for raw_tag in raw_tags:
                tags.append(raw_tag.string)


            cursor.execute(sql.SQL(
                        "INSERT INTO TASKS (ID, TITLE, TAGS, DESCRIPTION, URL) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (ID) DO "
                        "NOTHING"),
                        [progress, title, tags, description, f'https://freelance.habr.com{ref}'])
            connection.commit()


            print(f'{progress} / {len(tasks)}')

            progress += 1

        
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()



def check_new_tasks():
    pass


def select_tasks(filters) -> list[Task]:
    try:
        connection = psycopg2.connect(user="dude",
                                      password=password,
                                      host="localhost",
                                      port="5432",
                                      database="tasks")

        cursor = connection.cursor()


        cursor.execute(sql.SQL("SELECT * FROM TASKS WHERE CAST(%s as VARCHAR ARRAY) && TAGS"), [filters])
        connection.commit()

        records = cursor.fetchall()

        tasks = []
        
        for record in records:
            tasks.append(Task(record[1], record[2], record[3]))

        return tasks

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

