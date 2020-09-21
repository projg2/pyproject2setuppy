# vim:se fileencoding=utf-8 :
# (c) 2019 Michał Górny
# 2-clause BSD license

import unittest

from pyproject2setuppy.poetry import handle_poetry

from tests.base import BuildSystemTestCase


class PoetryTestCase(BuildSystemTestCase):
    """
    Tests for the poetry build system.
    """

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
        'entry_points': {},
        'package_data': {'': ['*']},
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

    handler = staticmethod(handle_poetry)


class PoetryBasicTest(unittest.TestCase, PoetryTestCase):
    """
    Test handling a simple poetry package.
    """

    pass


class PoetryHomepageTest(unittest.TestCase, PoetryTestCase):
    """
    Test handling a poetry package with homepage.
    """

    toml_extra = '''
homepage = "https://example.com"
'''

    expected_extra = {
        'url': 'https://example.com',
    }


class PoetryClassifiersTest(unittest.TestCase, PoetryTestCase):
    """
    Test handling a poetry package with trove classifiers.
    """

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
    """
    Test handling a poetry package with an explicit package list.
    """

    toml_extra = '''
packages = [
    { include = "test_package" },
]
'''

    expected_extra = {
        'package_dir': {},
    }


class PoetryExtraFilesTest(unittest.TestCase, PoetryTestCase):
    """
    Test handling a poetry package with non-Python files inside.
    """

    toml_extra = '''
packages = [
    { include = "test_package" },
]
'''

    expected_extra = {
        'package_dir': {},
    }
    expected_extra_files = [
        'test_package/VERSION',
    ]

    def make_package(self):
        d = super(PoetryExtraFilesTest, self).make_package()
        with open(self.expected_extra_files[0], 'w'):
            pass
        return d


class PoetryPackagesOtherTest(unittest.TestCase, PoetryTestCase):
    """
    Test handling a poetry package with two packages on the list.
    """

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
    """
    Test handling a poetry package with the other package on the list
    (verifying that autodetection does not trigger).
    """

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
    """
    Test that sdist format skips the package.
    """

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
    """
    Test that wheel format does not skip the package.
    """

    toml_extra = '''
packages = [
    { include = "test_package", format = "wheel" },
]
'''

    expected_extra = {
        'package_dir': {},
    }


class PoetryPackagesNestedTest(unittest.TestCase, PoetryTestCase):
    """
    Test handling nested packages.
    """

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
    """
    Test handling packages in a subdirectory ("from").
    """

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


class PoetryScriptsTest(unittest.TestCase, PoetryTestCase):
    """
    Test handling scripts.
    """

    toml_extra = '''
    [tool.poetry.scripts]
    test-tool = "testlib:main"
    '''

    expected_extra = {
        'entry_points': {
            'console_scripts': [
                'test-tool = testlib:main',
            ]
        }
    }


class PoetryPluginsTest(unittest.TestCase, PoetryTestCase):
    """
    Test handling plugins.
    """

    toml_extra = '''
    [tool.poetry.plugins."blogtool.parsers"]
    ".rst" = "some_module:SomeClass"
    '''

    expected_extra = {
        'entry_points': {
            'blogtool.parsers': [
                '.rst = some_module:SomeClass',
            ]
        }
    }


class PoetryPluginsAndScriptsTest(unittest.TestCase, PoetryTestCase):
    """
    Test handling plugins and scripts.
    """

    toml_extra = '''
    [tool.poetry.scripts]
    test-tool = "testlib:main"

    [tool.poetry.plugins."blogtool.parsers"]
    ".rst" = "some_module:SomeClass"
    '''

    expected_extra = {
        'entry_points': {
            'console_scripts': [
                'test-tool = testlib:main',
            ],
            'blogtool.parsers': [
                '.rst = some_module:SomeClass',
            ]
        }
    }
