# vim:se fileencoding=utf-8 :
# (c) 2019 Michał Górny
# 2-clause BSD license

import unittest

from pyproject2setuppy.poetry import handle_poetry

from tests.base import BuildSystemTestCase


class PoetryTestCase(BuildSystemTestCase):
    toml_base = '''
[build-system]
requires = ["poetry"]
build-backend = "poetry.masonry.api"

[tool.poetry]
name = "test_package"
version = "0"
description = "description."
authors = ["Some Guy <guy@example.com>"]
license = "MIT"
'''

    expected_base = {
        'name': 'test_package',
        'version': '0',
        'description': 'description.',
        'author': 'Some Guy',
        'author_email': 'guy@example.com',
        'packages': ['test_package'],
        'url': None,
        'classifiers': [],
    }

    package_files = [
        'test_package/__init__.py',
        'other_package/__init__.py',
        'nested_package/__init__.py',
        'nested_package/subpackage/__init__.py',
        'nested_package/subpackage/subsub/__init__.py',
        'src/subdir_package/__init__.py',
        'src/subdir_package/sub/__init__.py',
    ]

    module = 'pyproject2setuppy.poetry'
    handler = staticmethod(handle_poetry)


class PoetryBasicTest(unittest.TestCase, PoetryTestCase):
    pass


class PoetryHomepageTest(unittest.TestCase, PoetryTestCase):
    toml_extra = '''
homepage = "https://example.com"
'''

    expected_extra = {
        'url': 'https://example.com',
    }


class PoetryClassifiersTest(unittest.TestCase, PoetryTestCase):
    toml_extra = '''
classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3"
]
'''

    expected_extra = {
        'classifiers': [
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3"
        ],
    }


class PoetryPackagesTest(unittest.TestCase, PoetryTestCase):
    toml_extra = '''
packages = [
    { include = "test_package" },
]
'''

    expected_extra = {
        'package_dir': {},
    }


class PoetryPackagesOtherTest(unittest.TestCase, PoetryTestCase):
    toml_extra = '''
packages = [
    { include = "test_package" },
    { include = "other_package" },
]
'''

    expected_extra = {
        'package_dir': {},
        'packages': ['test_package', 'other_package'],
    }


class PoetryPackagesOtherOnlyTest(unittest.TestCase, PoetryTestCase):
    toml_extra = '''
packages = [
    { include = "other_package" },
]
'''

    expected_extra = {
        'package_dir': {},
        'packages': ['other_package'],
    }


class PoetryPackagesOtherSdistTest(unittest.TestCase, PoetryTestCase):
    toml_extra = '''
packages = [
    { include = "test_package" },
    { include = "other_package", format = "sdist" },
]
'''

    expected_extra = {
        'package_dir': {},
        'packages': ['test_package'],
    }


class PoetryPackagesWheelTest(unittest.TestCase, PoetryTestCase):
    toml_extra = '''
packages = [
    { include = "test_package", format = "wheel" },
]
'''

    expected_extra = {
        'package_dir': {},
    }


class PoetryPackagesNestedTest(unittest.TestCase, PoetryTestCase):
    toml_extra = '''
packages = [
    { include = "nested_package" },
]
'''

    expected_extra = {
        'package_dir': {},
        'packages': [
            'nested_package',
            'nested_package.subpackage',
            'nested_package.subpackage.subsub'
        ],
    }


class PoetryPackagesSubdirTest(unittest.TestCase, PoetryTestCase):
    toml_extra = '''
packages = [
    { include = "subdir_package", from = "src" },
]
'''

    expected_extra = {
        'package_dir': {
            'subdir_package': 'src/subdir_package',
            'subdir_package.sub': 'src/subdir_package/sub',
        },
        'packages': [
            'subdir_package',
            'subdir_package.sub',
        ],
    }
