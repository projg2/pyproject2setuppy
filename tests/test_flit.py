# vim:se fileencoding=utf-8 :
# (c) 2019-2020 Michał Górny
# 2-clause BSD license

import unittest

from pyproject2setuppy.flit import handle_flit, handle_flit_thyself

from tests.base import BuildSystemTestCase


class FlitTestCase(BuildSystemTestCase):
    """
    Tests for the flit build system.
    """

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
        'entry_points': {},
        'package_data': {'': ['*']},
    }

    package_files = ['test_module.py']

    handler = staticmethod(handle_flit)

    def make_package(self):
        """
        Make a flit-compatible packags.  Adds docstring and version
        to the first .py file in package_files.
        """

        d = super(FlitTestCase, self).make_package()
        with open(self.package_files[0], 'w') as f:
            f.write('''
""" documentation. """
__version__ = '0'
''')
        return d


class FlitBasicTest(unittest.TestCase, FlitTestCase):
    """
    Test handling a simple flit package.
    """

    expected_extra = {
        'py_modules': ['test_module'],
    }


class FlitHomepageTest(unittest.TestCase, FlitTestCase):
    """
    Test handling a flit package with homepage.
    """

    toml_extra = '''
home-page = "https://example.com"
'''

    expected_extra = {
        'py_modules': ['test_module'],
        'url': 'https://example.com',
    }


class FlitClassifiersTest(unittest.TestCase, FlitTestCase):
    """
    Test handling a flit package with trove classifiers.
    """

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
    """
    Test handling a flit package containing a package instead of module.
    """

    package_files = ['test_module/__init__.py']

    expected_extra = {
        'packages': ['test_module']
    }


class FlitExtraFilesTest(unittest.TestCase, FlitTestCase):
    """
    Test handling a flit package with non-python files.
    """

    package_files = ['test_module/__init__.py',
                     'test_module/VERSION']

    expected_extra = {
        'packages': ['test_module'],
    }
    expected_extra_files = [
        'test_module/VERSION',
    ]


class FlitNestedPackageTest(unittest.TestCase, FlitTestCase):
    """
    Test handling a flit package containing nested packages.
    """

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


class FlitCoreTest(FlitTestCase):
    """Test for using flit_core backend"""

    toml_base = '''
[build-system]
requires = ["flit_core"]
build-backend = "flit_core.buildapi"

[tool.flit.metadata]
module = "test_module"
author = "Some Guy"
author-email = "guy@example.com"
'''


class FlitScriptsTest(unittest.TestCase, FlitTestCase):
    """Test handling scripts"""

    toml_extra = '''
[tool.flit.scripts]
test-tool = "testlib:main"
'''

    expected_extra = {
        'entry_points': {
            'console_scripts': [
                'test-tool = testlib:main',
            ]
        },
        'py_modules': ['test_module'],
    }


class FlitEntryPointsTest(unittest.TestCase, FlitTestCase):
    """Test handling entry points"""

    toml_extra = '''
[tool.flit.entrypoints."blogtool.parsers"]
".rst" = "some_module:SomeClass"
'''

    expected_extra = {
        'entry_points': {
            'blogtool.parsers': [
                '.rst = some_module:SomeClass',
            ]
        },
        'py_modules': ['test_module'],
    }


class FlitPluginsAndScriptsTest(unittest.TestCase, FlitTestCase):
    """Test handling plugins and scripts"""

    toml_extra = '''
[tool.flit.scripts]
test-tool = "testlib:main"

[tool.flit.entrypoints."blogtool.parsers"]
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
        },
        'py_modules': ['test_module'],
    }


class FlitSelfBuildTest(unittest.TestCase, BuildSystemTestCase):
    """Test for build_thyself backend in flit_core"""

    toml_base = '''
[build-system]
requires = []
build-backend = "fake_flit_core.build_thyself"
backend-path = "."
'''

    expected_base = {
        'name': 'fake_flit_core',
        'version': '0',
        'description': 'some text',
        'author': 'Some Guy',
        'author_email': 'guy@example.com',
        'url': 'https://example.com/',
        'classifiers': [
            'License :: OSI Approved :: BSD License',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        'packages': [
            'fake_flit_core',
        ],
    }

    handler = staticmethod(handle_flit_thyself)

    package_files = [
        'fake_flit_core/__init__.py',
        'fake_flit_core/build_thyself.py',
    ]

    @classmethod
    def make_expected(cls, args):
        return cls.package_files

    def make_package(self):
        d = super(FlitSelfBuildTest, self).make_package()
        with open(self.package_files[0], 'w') as f:
            f.write('''
""" documentation. """
__version__ = '0'
''')
        with open(self.package_files[1], 'w') as f:
            f.write('''
from . import __version__


class Metadata(object):
    """Emulate visible Metadata class behavior"""

    def __init__(self, mdict):
        self.name = mdict.pop('name')
        self.version = mdict.pop('version')
        self.summary = mdict.pop('summary')


metadata_dict_orig = {
    'name': 'fake_flit_core',
    'version': __version__,
    'author': 'Some Guy',
    'author_email': 'guy@example.com',
    'home_page': 'https://example.com/',
    'summary': 'some text',
    'requires_dist': [
        'pytoml',
    ],
    'requires_python': '>=3.4',
    'classifiers': [
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
}
metadata_dict = dict(metadata_dict_orig)
metadata = Metadata(metadata_dict)


def build_wheel(wheel_directory):
    try:
        from flit_core.common import Metadata, Module
        from flit_core.wheel import WheelBuilder
    except ImportError:
        import unittest
        raise unittest.SkipTest('Required flit package missing')

    import os.path
    from pathlib import Path

    whl_path = os.path.join(wheel_directory, 'test.whl')
    with open(whl_path, 'w+b') as fp:
        wb = WheelBuilder(
            Path.cwd(),
            Module('fake_flit_core', Path.cwd()),
            Metadata(metadata_dict_orig),
            entrypoints={},
            target_fp=fp
        )
        wb.build()
    return whl_path
''')
        return d
