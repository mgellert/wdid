import argparse
import os
import sqlite3
from dataclasses import dataclass
from datetime import date
from typing import Optional, List

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'db.sqlite3')


@dataclass
class Task:
    id: int
    date: date
    task: str
    done: bool

    @classmethod
    def from_tuple(cls, tuple: tuple) -> 'Task':
        return Task(tuple[0], date.fromisoformat(tuple[1]), tuple[2], tuple[3] == 1)


class TaskService:
    SCHEMA = """
        CREATE TABLE IF NOT EXISTS tasks (
            id integer PRIMARY KEY,
            date text NOT NULL,
            task text NOT NULL,
            done integer DEFAULT 0
        );
    """

    INSERT_TASK = """
        INSERT INTO tasks(date, task) values (?, ?);
    """

    COUNT_TASKS = """
        SELECT COUNT(*) FROM tasks;
    """

    UPDATE_TASK = """
        UPDATE tasks SET done = ? WHERE id = ?;
    """

    GET_TASK_BY_ID = """
        SELECT * FROM tasks WHERE id = ?;
    """

    GET_ALL_TASKS_FOR_DAY = """
        SELECT * FROM tasks WHERE date = ?;
    """

    def __init__(self, db_path: str = DEFAULT_PATH):
        self.connection = sqlite3.connect(db_path)

    def close_connection(self):
        self.connection.close()

    def create_schema(self):
        cursor = self.connection.cursor()
        cursor.execute(TaskService.SCHEMA)

    def insert_task(self, name: str, date: date = date.today()) -> int:
        cur = self.connection.cursor()
        cur.execute(TaskService.INSERT_TASK, (date, name))
        self.connection.commit()
        return cur.lastrowid

    def update_task(self, task_id: int, done: bool = True):
        cur = self.connection.cursor()
        cur.execute(TaskService.UPDATE_TASK, (done, task_id))
        self.connection.commit()

    def count_tasks(self) -> int:
        (count,) = self.connection.execute(TaskService.COUNT_TASKS).fetchone()
        return count

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        cur = self.connection.cursor()
        cur.execute(TaskService.GET_TASK_BY_ID, (task_id,))
        row = cur.fetchone()
        if row is None:
            return None
        return Task.from_tuple(row)

    def get_tasks_for_date(self, date: date = date.today()) -> List[Task]:
        cur = self.connection.cursor()
        cur.execute(TaskService.GET_ALL_TASKS_FOR_DAY, (date,))
        all_tasks = cur.fetchall()
        return [Task.from_tuple(task) for task in all_tasks]


if __name__ == '__main__':
    task_service = TaskService()

    parser = argparse.ArgumentParser(prog='wdid',
                                     description='What did I do? A personal task list manager.',
                                     allow_abbrev=False)
    parser.add_argument('-t', '--today', action='store_const', const='today', help='today\'s tasks')
    args = parser.parse_args()

    if args.today:
        task_service.get_tasks_for_date()

    task_service.close_connection()
