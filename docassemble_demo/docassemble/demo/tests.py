# do not pre-load
import unittest
from docassemble.demo.change_suffix import my_name_suffix


class TestNameSuffix(unittest.TestCase):

    def setUp(self):
        pass

    def test_jr(self):
        self.assertIn('Jr', my_name_suffix())

    def test_length(self):
        self.assertEqual(len(my_name_suffix()), 7)

if __name__ == '__main__':
    unittest.main()
