import argparse
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Dict

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
        SELECT id, date, task, done FROM tasks WHERE id = ?;
    """

    GET_ALL_TASKS_FOR_DAY = """
        SELECT id, date, task, done FROM tasks WHERE date = ? ORDER BY date ASC;
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

    def get_tasks_for_date(self, date: date = date.today()) -> Dict[date, List[Task]]:
        cur = self.connection.cursor()
        cur.execute(TaskService.GET_ALL_TASKS_FOR_DAY, (date,))
        tasks = [Task.from_tuple(task) for task in cur.fetchall()]
        return TaskService._group_tasks_by_date(tasks)

    # TODO look into itertools groupby
    @staticmethod
    def _group_tasks_by_date(tasks: List[Task]) -> Dict[date, List[Task]]:
        group_by_date = {}
        for task in tasks:
            if task.date not in group_by_date:
                group_by_date[task.date] = []
            group_by_date[task.date].append(task)
        return group_by_date


def task_printer(tasks: Dict[date, List[Task]]):
    for date in tasks.keys():
        print(date.strftime("%Y-%m-%d, %A"))
        for task in tasks[date]:
            done_symbol = "\u2714" if task.done else "\u2718"
            print(f"  {done_symbol} {task.task} ({task.id})")


def parse_args(args: List[str]):
    parser = argparse.ArgumentParser(prog='wdid', description='What did I do? A personal task list manager.')
    subparsers = parser.add_subparsers(dest='command')

    # commands
    list_command = subparsers.add_parser('list', help='list tasks for different day(s)')

    add_command = subparsers.add_parser('add', help='add task for a certain day')
    add_command.add_argument('-n', '--name', action='store', help='name of the task', required=True)
    add_command.add_argument('-d', '--date', action='store', help='date of the task')

    update_command = subparsers.add_parser('update', help='update the specified task')
    update_command.add_argument('id', action='store', help='id of the task', type=int)

    return parser.parse_args(args)


def main(sys_args: List[str], db_path: str = DEFAULT_PATH):
    task_service = TaskService(db_path)
    task_service.create_schema()

    args = parse_args(sys_args)

    if args.command == 'list':
        tasks = task_service.get_tasks_for_date()
        task_printer(tasks)
    elif args.command == 'add':
        task_service.insert_task(args.name)
    elif args.command == 'up':
        task = task_service.get_task_by_id(args.id)
        if not task:
            print(f"Task with id {args.id} does not exist!")
        else:
            task_service.update_task(args.id, not task.done)

    task_service.close_connection()


if __name__ == '__main__':
    main(sys.argv[1:])
