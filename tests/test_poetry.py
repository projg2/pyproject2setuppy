# vim:se fileencoding=utf-8 :
# (c) 2019 Michał Górny
# 2-clause BSD license

import os
import tempfile
import toml
import unittest
import unittest.mock

from pyproject2setuppy.poetry import handle_poetry


TOML_COMMON = '''
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


ARGS_COMMON = {
    'name': 'test_package',
    'version': '0',
    'description': 'description.',
    'author': 'Some Guy',
    'author_email': 'guy@example.com',
    'packages': ['test_package'],
}


def make_package():
    d = tempfile.TemporaryDirectory()
    os.chdir(d.name)
    for subdir in ('test_package', 'other_package'):
        os.mkdir(subdir)
        with open('{}/__init__.py'.format(subdir), 'w') as f:
            pass
    return d


@unittest.mock.patch('pyproject2setuppy.poetry.setup')
class PoetryTest(unittest.TestCase):
    def test_basic(self, mock_setup):
        metadata = toml.loads(TOML_COMMON)
        with make_package():
            handle_poetry(metadata)
            mock_setup.assert_called_with(
                    url=None,
                    classifiers=[],
                    **ARGS_COMMON)

    def test_homepage(self, mock_setup):
        metadata = toml.loads(TOML_COMMON + '''
homepage = "https://example.com"
''')
        with make_package():
            handle_poetry(metadata)
            mock_setup.assert_called_with(
                    url='https://example.com',
                    classifiers=[],
                    **ARGS_COMMON)

    def test_classifiers(self, mock_setup):
        metadata = toml.loads(TOML_COMMON + '''
classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3"
]
''')
        with make_package():
            handle_poetry(metadata)
            mock_setup.assert_called_with(
                    url=None,
                    classifiers=[
                        "License :: OSI Approved :: MIT License",
                        "Programming Language :: Python :: 2",
                        "Programming Language :: Python :: 3"
                    ],
                    **ARGS_COMMON)

    def test_packages(self, mock_setup):
        metadata = toml.loads(TOML_COMMON + '''
packages = [
    { include = "test_package" },
]
''')
        with make_package():
            handle_poetry(metadata)
            mock_setup.assert_called_with(
                    url=None,
                    classifiers=[],
                    **ARGS_COMMON)

    def test_packages_other(self, mock_setup):
        metadata = toml.loads(TOML_COMMON + '''
packages = [
    { include = "test_package" },
    { include = "other_package" },
]
''')
        with make_package():
            handle_poetry(metadata)
            args = ARGS_COMMON.copy()
            del args['packages']
            mock_setup.assert_called_with(
                    url=None,
                    classifiers=[],
                    packages=['test_package', 'other_package'],
                    **args)

    def test_packages_other_only(self, mock_setup):
        metadata = toml.loads(TOML_COMMON + '''
packages = [
    { include = "other_package" },
]
''')
        with make_package():
            handle_poetry(metadata)
            args = ARGS_COMMON.copy()
            del args['packages']
            mock_setup.assert_called_with(
                    url=None,
                    classifiers=[],
                    packages=['other_package'],
                    **args)

    def test_packages_sdist_other(self, mock_setup):
        metadata = toml.loads(TOML_COMMON + '''
packages = [
    { include = "test_package" },
    { include = "other_package", format = "sdist" },
]
''')
        with make_package():
            handle_poetry(metadata)
            mock_setup.assert_called_with(
                    url=None,
                    classifiers=[],
                    **ARGS_COMMON)

    def test_packages_wheel(self, mock_setup):
        metadata = toml.loads(TOML_COMMON + '''
packages = [
    { include = "test_package", format = "wheel" },
]
''')
        with make_package():
            handle_poetry(metadata)
            mock_setup.assert_called_with(
                    url=None,
                    classifiers=[],
                    **ARGS_COMMON)
