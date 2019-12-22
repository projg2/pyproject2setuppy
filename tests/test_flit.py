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

from pyproject2setuppy.flit import handle_flit


TOML_COMMON = '''
[build-system]
requires = ["flit"]
build-backend = "flit.buildapi"

[tool.flit.metadata]
module = "test_module"
author = "Some Guy"
author-email = "guy@example.com"
'''


ARGS_COMMON = {
    'name': 'test_module',
    'version': '0',
    'description': 'documentation.',
    'author': 'Some Guy',
    'author_email': 'guy@example.com',
    'py_modules': ['test_module'],
}


def make_package():
    d = TemporaryDirectory()
    os.chdir(d.name)
    with open('test_module.py', 'w') as f:
        f.write('''
""" documentation. """
__version__ = '0'
''')
    return d


@patch('pyproject2setuppy.flit.setup')
class FlitTest(unittest.TestCase):
    def test_basic(self, mock_setup):
        metadata = toml.loads(TOML_COMMON)
        with make_package():
            handle_flit(metadata)
            mock_setup.assert_called_with(
                    url=None,
                    classifiers=[],
                    **ARGS_COMMON)

    def test_homepage(self, mock_setup):
        metadata = toml.loads(TOML_COMMON + '''
home-page = "https://example.com"
''')
        with make_package():
            handle_flit(metadata)
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
            handle_flit(metadata)
            mock_setup.assert_called_with(
                    url=None,
                    classifiers=[
                        "License :: OSI Approved :: MIT License",
                        "Programming Language :: Python :: 2",
                        "Programming Language :: Python :: 3"
                    ],
                    **ARGS_COMMON)
