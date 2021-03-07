import os
import unittest

from wdid import create_connection, create_schema, insert_task, count_tasks, update_task, get_task_by_id

TEST_DATABASE = os.path.join(os.path.dirname(__file__), 'test.sqlite3')


class DatabaseTests(unittest.TestCase):

    def setUp(self):
        self.connection = create_connection(TEST_DATABASE)
        create_schema(self.connection)

    def test_schema_creation(self):
        count = count_tasks(self.connection)
        self.assertEqual(count, 0)

    def test_insert_task(self):
        task_id = insert_task(self.connection, "Foo")
        self.assertEqual(task_id, 1)

        task_id = insert_task(self.connection, "Bar")
        self.assertEqual(task_id, 2)

        count = count_tasks(self.connection)
        self.assertEqual(count, 2)

    def test_update_task(self):
        task_id = insert_task(self.connection, "Foo")
        update_task(self.connection, task_id)
        task = get_task_by_id(self.connection, task_id)
        self.assertEqual(task.id, 1)
        self.assertTrue(task.done)

    def test_get_non_existing_task(self):
        task = get_task_by_id(self.connection, 1)
        self.assertIsNone(task)

    def tearDown(self):
        self.connection.close()
        os.remove(TEST_DATABASE)


if __name__ == '__main__':
    unittest.main()
