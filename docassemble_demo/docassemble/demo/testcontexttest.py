# do not pre-load
import unittest
from docassemble.base.util import path_and_mimetype, url_of


class TestNameSuffix(unittest.TestCase):

    def setUp(self):
        pass

    def test_path(self):
        (path, mimetype) = path_and_mimetype('lithuania.svg')
        self.assertTrue(path.endswith('site-packages/docassemble/demo/data/static/lithuania.svg'))
        self.assertEqual(mimetype, 'image/svg+xml')

    def test_url(self):
        self.assertTrue(url_of('lithuania.svg').startswith('/packagestatic/docassemble.demo/lithuania.svg'))

if __name__ == '__main__':
    from docassemble.webapp.server import TestContext
    with TestContext('docassemble.demo'):
        unittest.main()
