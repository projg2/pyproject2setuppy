# vim:se fileencoding=utf-8 :
# (c) 2019 Michał Górny
# 2-clause BSD license

import os
import sys
import unittest

from pyproject2setuppy.common import auto_find_packages

from tests.base import TestDirectory


class AutoFindPackagesTest(unittest.TestCase):
    """
    Test cases for auto_find_packages() function.
    """

    def test_module(self):
        """ Test finding a plain .py module. """

        with TestDirectory() as d:
            with open('test_module.py', 'w') as f:
                pass
            self.assertEqual(
                    auto_find_packages('test_module'),
                    {'py_modules': ['test_module']})

    def test_package(self):
        """ Test finding a flat package. """

        with TestDirectory() as d:
            os.mkdir('test_package')
            with open('test_package/__init__.py', 'w') as f:
                pass
            self.assertEqual(
                    auto_find_packages('test_package'),
                    {'packages': ['test_package']})

    def test_package_deep(self):
        """ Test finding a package with a subpackage. """

        with TestDirectory() as d:
            for subdir in ('test_package', 'test_package/subpackage'):
                os.mkdir(subdir)
                with open('{}/__init__.py'.format(subdir), 'w') as f:
                    pass
            self.assertEqual(
                    auto_find_packages('test_package'),
                    {'packages': ['test_package', 'test_package.subpackage']})
