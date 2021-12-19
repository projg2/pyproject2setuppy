# vim:se fileencoding=utf-8 :
# (c) 2019-2021 Michał Górny
# 2-clause BSD license

import unittest

from pyproject2setuppy.flit import handle_flit

from tests.base import BuildSystemTestCase


class FlitTestCase(BuildSystemTestCase):
    """
    Tests for the flit build system.
    """

    toml_base = '''
[build-system]
requires = ["flit"]
build-backend = "flit.buildapi"

[project]
name = "test_module"
authors = [
    {name="Some Guy", email="guy@example.com"},
]
dynamic = ["version", "description"]
'''

    expected_base = {
        'name': 'test_module',
        'version': '0',
        'description': 'documentation.',
        'author': 'Some Guy',
        'author_email': 'guy@example.com',
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


class FlitVersionTest(unittest.TestCase, FlitTestCase):
    """
    Test handling a package with non-dynamic version.
    """

    toml_base = '''
[build-system]
requires = ["flit"]
build-backend = "flit.buildapi"

[project]
name = "test_module"
version = "0"
authors = [
    {name="Some Guy", email="guy@example.com"},
]
dynamic = ["description"]
'''

    expected_extra = {
        'py_modules': ['test_module'],
    }


class FlitDescriptionTest(unittest.TestCase, FlitTestCase):
    """
    Test handling a package with non-dynamic description.
    """

    toml_base = '''
[build-system]
requires = ["flit"]
build-backend = "flit.buildapi"

[project]
name = "test_module"
description = "documentation."
authors = [
    {name="Some Guy", email="guy@example.com"},
]
dynamic = ["version"]
'''

    expected_extra = {
        'py_modules': ['test_module'],
    }


class FlitVersionDescriptionTest(unittest.TestCase, FlitTestCase):
    """
    Test handling a package with non-dynamic version and description.
    """

    toml_base = '''
[build-system]
requires = ["flit"]
build-backend = "flit.buildapi"

[project]
name = "test_module"
version = "0"
description = "documentation."
authors = [
    {name="Some Guy", email="guy@example.com"},
]
'''

    expected_extra = {
        'py_modules': ['test_module'],
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

[project]
name = "test_module"
authors = [
    {name="Some Guy", email="guy@example.com"},
]
dynamic = ["version", "description"]
'''


class FlitScriptsTest(unittest.TestCase, FlitTestCase):
    """Test handling scripts"""

    toml_extra = '''
[project.scripts]
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


class FlitGUIScriptsTest(unittest.TestCase, FlitTestCase):
    """Test handling scripts"""

    toml_extra = '''
[project.gui-scripts]
test-tool = "testlib:main"
'''

    expected_extra = {
        'entry_points': {
            'gui_scripts': [
                'test-tool = testlib:main',
            ]
        },
        'py_modules': ['test_module'],
    }


class FlitEntryPointsTest(unittest.TestCase, FlitTestCase):
    """Test handling entry points"""

    toml_extra = '''
[project.entrypoints."blogtool.parsers"]
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
[project.scripts]
test-tool = "testlib:main"

[project.entrypoints."blogtool.parsers"]
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


class FlitImplicitSubdirTest(unittest.TestCase, FlitTestCase):
    """Test handling implicit src/ with module.name."""

    package_files = [
        'src/subdir_package/__init__.py',
        'src/subdir_package/sub/__init__.py',
    ]

    toml_extra = '''
[tool.flit.module]
name = "subdir_package"
'''

    expected_extra = {
        'package_dir': {
            '': 'src',
        },
        'packages': [
            'subdir_package',
            'subdir_package.sub',
        ],
    }


class FlitIrrelevantToolFlitSectionTest(unittest.TestCase, FlitTestCase):
    """Test ignoring tool.flit with no relevant keys"""

    toml_extra = '''
[tool.flit.sdist]
exclude = ["*"]
'''

    expected_extra = {
        'py_modules': ['test_module'],
    }


class FlitDuplicateMetadataTest(unittest.TestCase, FlitTestCase):
    """Test ignoring tool.flit with no relevant keys"""

    toml_extra = '''
[tool.flit.metadata]
module = "test_module"
author = "Some Guy"
author-email = "guy@example.com"
'''

    expect_exception = ValueError
