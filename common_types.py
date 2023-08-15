import datetime

class Task:
    def __init__(self, source, message) -> None:
        self.source = source
        self.message = message

    def __eq__(self, __value: object) -> bool:
        return self.source == object.source and self.message == object.message
    
class User:
    def __init__(self, id, filters) -> None:
        self.id = id
        self.filters = filters

class Config:
    def __init__(self) -> None:
        with open('../config.txt', 'r') as token_file:
            lines = token_file.readlines()
            self.token = lines[0].strip()

def init_global() -> None:
    global last_inserted_task
    last_inserted_task = datetime.datetime.now()