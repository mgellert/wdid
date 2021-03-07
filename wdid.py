import os
import sqlite3
from dataclasses import dataclass
from datetime import date
from sqlite3 import Connection, Error
from typing import Optional

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

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


@dataclass
class Task:
    id: int
    date: date
    task: str
    done: bool

    @classmethod
    def from_tuple(cls, tuple: tuple) -> 'Task':
        return Task(tuple[0], date.fromisoformat(tuple[1]), tuple[2], tuple[3] == 1)


def create_connection(db_path: str = DEFAULT_PATH) -> Connection:
    try:
        return sqlite3.connect(db_path)
    except Error as e:
        print("Error connecting to database:", e)


def create_schema(conn: Connection):
    cursor = conn.cursor()
    cursor.execute(SCHEMA)


def insert_task(conn: Connection, name: str, date: date = date.today()) -> int:
    cur = conn.cursor()
    cur.execute(INSERT_TASK, (date, name))
    conn.commit()
    return cur.lastrowid


def update_task(conn: Connection, task_id: int, done: bool = True):
    cur = conn.cursor()
    cur.execute(UPDATE_TASK, (done, task_id))
    conn.commit()


def count_tasks(conn: Connection) -> int:
    (count,) = conn.execute(COUNT_TASKS).fetchone()
    return count


def get_task_by_id(conn: Connection, task_id: int) -> Optional[Task]:
    cur = conn.cursor()
    cur.execute(GET_TASK_BY_ID, (task_id,))
    row = cur.fetchone()
    if row is None:
        return None
    return Task.from_tuple(row)


if __name__ == '__main__':
    connection = create_connection()
    create_schema(connection)
    connection.close()
