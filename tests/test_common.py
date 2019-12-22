# vim:se fileencoding=utf-8 :
# (c) 2019 Michał Górny
# 2-clause BSD license

import os
import tempfile
import unittest

from pyproject2setuppy.common import auto_find_packages


class AutoFindPackagesTest(unittest.TestCase):
    def test_module(self):
        with tempfile.TemporaryDirectory() as d:
            os.chdir(d)
            with open('test_module.py', 'w') as f:
                pass
            self.assertEqual(
                    auto_find_packages('test_module'),
                    {'py_modules': ['test_module']})

    def test_package(self):
        with tempfile.TemporaryDirectory() as d:
            os.chdir(d)
            os.mkdir('test_package')
            with open('test_package/__init__.py', 'w') as f:
                pass
            self.assertEqual(
                    auto_find_packages('test_package'),
                    {'packages': ['test_package']})

    def test_package_deep(self):
        with tempfile.TemporaryDirectory() as d:
            os.chdir(d)
            for subdir in ('test_package', 'test_package/subpackage'):
                os.mkdir(subdir)
                with open('{}/__init__.py'.format(subdir), 'w') as f:
                    pass
            self.assertEqual(
                    auto_find_packages('test_package'),
                    {'packages': ['test_package', 'test_package.subpackage']})
