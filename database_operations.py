import psycopg2
from psycopg2 import Error
from psycopg2 import sql
from common_types import Config

def createTasksTable(config : Config) -> None:
    try:
        connection = psycopg2.connect(user=config.database_user, password=config.password, host=config.host, port=config.port, database=config.database)

        cursor = connection.cursor()

        cursor.execute(sql.SQL(
            "CREATE TABLE IF NOT EXISTS TASKS (ID BIGINT PRIMARY KEY NOT NULL, TITLE VARCHAR NOT NULL, TAGS VARCHAR ARRAY, DESCRIPTION VARCHAR, URL VARCHAR, PUBLISH_TIME TIMESTAMP)"))
        connection.commit()

    except (Exception, Error) as error:
        print("Error while working with PostgreSQL: ", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

def insert_task(cursor, connection, title, tags, description, ref, pub_time) -> None:
    cursor.execute(sql.SQL(
                        "INSERT INTO TASKS (ID, TITLE, TAGS, DESCRIPTION, URL, PUBLISH_TIME) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (ID) DO "
                        "NOTHING"),
                        [hash(title), title, tags, description, f'https://freelance.habr.com{ref}', pub_time])
    connection.commit()