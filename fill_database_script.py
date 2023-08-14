import habr_parser
import database_operations
from common_types import Config

config = Config()
database_operations.createTasksTable(config)
habr_parser.fill_tasks_table(config)