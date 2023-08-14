class Task:
    def __init__(self, title, tags, description, url, publish_date) -> None:
        self.title = title
        self.tags = tags
        self.description = description
        self.url = url
        self.publish_date = publish_date

    def __eq__(self, __value: object) -> bool:
        return self.title == object.title
    
class User:
    def __init__(self, id, filters) -> None:
        self.id = id
        self.filters = filters

class Config:
    def __init__(self) -> None:
        with open('../config.txt', 'r') as token_file:
            lines = token_file.readlines()
            self.token = lines[0].strip()
            self.database_user = lines[1].strip()
            self.password = lines[2].strip()
            self.host = lines[3].strip()
            self.port = lines[4].strip()
            self.database = lines[5].strip()