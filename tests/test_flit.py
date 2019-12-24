# vim:se fileencoding=utf-8 :
# (c) 2019 Michał Górny
# 2-clause BSD license

import unittest

from pyproject2setuppy.flit import handle_flit

from tests.base import BuildSystemTestCase


class FlitTestCase(BuildSystemTestCase):
    toml_base = '''
[build-system]
requires = ["flit"]
build-backend = "flit.buildapi"

[tool.flit.metadata]
module = "test_module"
author = "Some Guy"
author-email = "guy@example.com"
'''

    expected_base = {
        'name': 'test_module',
        'version': '0',
        'description': 'documentation.',
        'author': 'Some Guy',
        'author_email': 'guy@example.com',
        'url': None,
        'classifiers': [],
    }

    package_files = ['test_module.py']

    module = 'pyproject2setuppy.flit'
    handler = staticmethod(handle_flit)

    def make_package(self):
        d = super(FlitTestCase, self).make_package()
        with open(self.package_files[0], 'w') as f:
            f.write('''
""" documentation. """
__version__ = '0'
''')
        return d


class FlitBasicTest(unittest.TestCase, FlitTestCase):
    expected_extra = {
        'py_modules': ['test_module'],
    }


class FlitHomepageTest(unittest.TestCase, FlitTestCase):
    toml_extra = '''
home-page = "https://example.com"
'''

    expected_extra = {
        'py_modules': ['test_module'],
        'url': 'https://example.com',
    }


class FlitClassifiersTest(unittest.TestCase, FlitTestCase):
    toml_extra = '''
classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3"
]
'''

    expected_extra = {
        'py_modules': ['test_module'],
        'classifiers': [
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3"
        ],
    }


class FlitPackageTest(unittest.TestCase, FlitTestCase):
    package_files = ['test_module/__init__.py']

    expected_extra = {
        'packages': ['test_module']
    }


class FlitNestedPackageTest(unittest.TestCase, FlitTestCase):
    package_files = [
        'test_module/__init__.py',
        'test_module/sub_module/__init__.py',
        'test_module/sub_module/subsub/__init__.py',
    ]

    expected_extra = {
        'packages': [
            'test_module',
            'test_module.sub_module',
            'test_module.sub_module.subsub',
        ]
    }
