import io
import os
import unittest
from contextlib import redirect_stdout

from wdid import main

TEST_DATABASE = os.path.join(os.path.dirname(__file__), 'test.sqlite3')


class IntegrationTests(unittest.TestCase):

    def test_add_task_for_today_and_list(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            main(['add', '-n', 'foo bar baz'], TEST_DATABASE)
            main(['list'], TEST_DATABASE)
            self.assertRegex(buf.getvalue(), r"\d{4}-\d{2}-\d{2}, \w+\n  ✘ foo bar baz \(\d\)\n")

    def tearDown(self):
        os.remove(TEST_DATABASE)


if __name__ == '__main__':
    unittest.main()
