# vim:se fileencoding=utf-8 :
# (c) 2019 Michał Górny
# 2-clause BSD license

import os
import sys
import toml
import unittest

if sys.hexversion >= 0x03000000:
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
else:
    from backports.tempfile import TemporaryDirectory
    from mock import patch

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
    d = TemporaryDirectory()
    os.chdir(d.name)
    os.mkdir('src')
    for subdir in ('test_package', 'other_package', 'nested_package',
                   'nested_package/subpackage',
                   'nested_package/subpackage/subsub',
                   'src/subdir_package',
                   'src/subdir_package/sub'):
        os.mkdir(subdir)
        with open('{}/__init__.py'.format(subdir), 'w') as f:
            pass
    return d


@patch('pyproject2setuppy.poetry.setup')
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
                    package_dir={},
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
                    package_dir={},
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
                    package_dir={},
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
                    package_dir={},
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
                    package_dir={},
                    **ARGS_COMMON)

    def test_packages_nested(self, mock_setup):
        metadata = toml.loads(TOML_COMMON + '''
packages = [
    { include = "nested_package" },
]
''')
        with make_package():
            handle_poetry(metadata)
            args = ARGS_COMMON.copy()
            del args['packages']
            mock_setup.assert_called_with(
                    url=None,
                    classifiers=[],
                    packages=['nested_package',
                              'nested_package.subpackage',
                              'nested_package.subpackage.subsub'],
                    package_dir={},
                    **args)

    def test_packages_subdir(self, mock_setup):
        metadata = toml.loads(TOML_COMMON + '''
packages = [
    { include = "subdir_package", from = "src" },
]
''')
        with make_package():
            handle_poetry(metadata)
            args = ARGS_COMMON.copy()
            del args['packages']
            mock_setup.assert_called_with(
                    url=None,
                    classifiers=[],
                    packages=['subdir_package',
                              'subdir_package.sub'],
                    package_dir={
                        'subdir_package': 'src/subdir_package',
                        'subdir_package.sub': 'src/subdir_package/sub',
                    },
                    **args)
