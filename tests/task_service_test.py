import os
import unittest
from datetime import date

from wdid import TaskService

TEST_DATABASE = os.path.join(os.path.dirname(__file__), 'test.sqlite3')


class TaskServiceTests(unittest.TestCase):

    def setUp(self):
        self.service = TaskService(TEST_DATABASE)
        self.service.create_schema()

    def test_schema_creation(self):
        count = self.service.count_tasks()
        self.assertEqual(count, 0)

    def test_insert_task(self):
        task_id = self.service.insert_task("Foo")
        self.assertEqual(task_id, 1)

        task_id = self.service.insert_task("Bar")
        self.assertEqual(task_id, 2)

        count = self.service.count_tasks()
        self.assertEqual(count, 2)

    def test_update_task(self):
        task_id = self.service.insert_task("Foo")
        self.service.update_task(task_id)
        task = self.service.get_task_by_id(task_id)
        self.assertEqual(task.id, 1)
        self.assertTrue(task.done)

    def test_get_non_existing_task(self):
        task = self.service.get_task_by_id(1)
        self.assertIsNone(task)

    def test_get_tasks_for_day(self):
        self.service.insert_task("Foo", date(2021, 1, 3))
        self.service.insert_task("Bar", date(2021, 1, 4))
        self.service.insert_task("Baz", date(2021, 1, 4))
        self.service.insert_task("Foo", date(2021, 1, 5))

        tasks = self.service.get_tasks_for_date(date(2021, 1, 4))
        self.assertEqual(list(tasks.keys()), [date(2021, 1, 4)])
        for task in tasks[date(2021, 1, 4)]:
            self.assertEqual(task.date, date(2021, 1, 4))

    def tearDown(self):
        self.service.close_connection()
        os.remove(TEST_DATABASE)


if __name__ == '__main__':
    unittest.main()
