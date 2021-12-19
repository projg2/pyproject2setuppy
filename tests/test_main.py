# vim:se fileencoding=utf-8 :
# (c) 2019-2020 Michał Górny
# 2-clause BSD license

import sys
import unittest

if sys.hexversion >= 0x03000000:
    from unittest.mock import patch
else:
    from mock import patch

from pyproject2setuppy.main import main

from tests.base import TestDirectory


def make_pyproject_toml(data):
    """
    Create a temporary test directory with pyproject.toml containing
    specified string data.
    """

    d = TestDirectory()
    with open('pyproject.toml', 'w') as f:
        f.write(data)
    return d


class MainUnitTest(unittest.TestCase):
    """
    Unit tests for the main() function.
    """

    @patch('pyproject2setuppy.flit.handle_flit')
    def test_flit(self, handler_mock):
        """
        Test that flit handler is triggered correctly.
        """

        data = '''
[build-system]
requires = ["flit"]
build-backend = "flit.buildapi"
'''
        with make_pyproject_toml(data):
            main()
            self.assertTrue(handler_mock.called)

    @patch('pyproject2setuppy.flit.handle_flit')
    def test_flit_core(self, handler_mock):
        """
        Test that flit-core handler is triggered correctly.
        """

        data = '''
[build-system]
requires = ["flit_core"]
build-backend = "flit_core.buildapi"
'''
        with make_pyproject_toml(data):
            main()
            self.assertTrue(handler_mock.called)

    @patch('pyproject2setuppy.poetry.handle_poetry')
    def test_poetry(self, handler_mock):
        """
        Test that poetry handler is triggered correctly.
        """

        data = '''
[build-system]
requires = ["poetry"]
build-backend = "poetry.masonry.api"
'''
        with make_pyproject_toml(data):
            main()
            self.assertTrue(handler_mock.called)

    @patch('pyproject2setuppy.poetry.handle_poetry')
    def test_poetry_core(self, handler_mock):
        """
        Test that poetry.core handler is triggered correctly.
        """

        data = '''
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
'''
        with make_pyproject_toml(data):
            main()
            self.assertTrue(handler_mock.called)

    @patch('pyproject2setuppy.setuptools.handle_setuptools')
    def test_setuptools(self, handler_mock):
        """
        Test that the setuptools handler is triggered correctly.
        """

        data = '''
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
'''
        with make_pyproject_toml(data):
            main()
            self.assertTrue(handler_mock.called)

    @patch('pyproject2setuppy.setuptools.handle_setuptools')
    def test_setuptools_legacy(self, handler_mock):
        """
        Test that the legacy setuptools handler is triggered correctly.
        """

        data = '''
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta:__legacy__"
'''
        with make_pyproject_toml(data):
            main()
            self.assertTrue(handler_mock.called)

    def test_garbage(self):
        """
        Test that unknown backend results in an exception.
        """

        data = '''
[build-system]
build-backend = "pyproject2setuppy.garbage"
'''
        with make_pyproject_toml(data):
            self.assertRaises(NotImplementedError, main)
