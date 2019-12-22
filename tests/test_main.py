# vim:se fileencoding=utf-8 :
# (c) 2019 Michał Górny
# 2-clause BSD license

import os
import tempfile
import unittest

from pyproject2setuppy.main import main


def make_pyproject_toml(data):
    d = tempfile.TemporaryDirectory()
    os.chdir(d.name)
    with open('pyproject.toml', 'w') as f:
        f.write(data)
    return d


class MainUnitTest(unittest.TestCase):
    @unittest.mock.patch('pyproject2setuppy.flit.handle_flit')
    def test_flit(self, handler_mock):
        data = '''
[build-system]
requires = ["flit"]
build-backend = "flit.buildapi"
'''
        with make_pyproject_toml(data):
            main()
            self.assertTrue(handler_mock.called)

    @unittest.mock.patch('pyproject2setuppy.poetry.handle_poetry')
    def test_poetry(self, handler_mock):
        data = '''
[build-system]
requires = ["poetry"]
build-backend = "poetry.masonry.api"
'''
        with make_pyproject_toml(data):
            main()
            self.assertTrue(handler_mock.called)

    def test_garbage(self):
        data = '''
[build-system]
build-backend = "pyproject2setuppy.garbage"
'''
        with make_pyproject_toml(data):
            self.assertRaises(NotImplementedError, main)
