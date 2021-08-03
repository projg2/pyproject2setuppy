# vim:se fileencoding=utf-8 :
# (c) 2019-2021 Michał Górny
# 2-clause BSD license

import sys
import unittest

try:
    import tomli as toml
except ImportError:
    import toml

from pyproject2setuppy.setuptools import handle_setuptools

from tests.base import BuildSystemTestCase, patch


class SetuptoolsTestCase(BuildSystemTestCase):
    """
    Tests for the setuptools build system.
    """

    toml_base = '''
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"
'''

    # cheap hack: expected_base goes into [metadata], expected_extra
    # into [options]
    expected_base = {
        'name': 'test_module',
        'version': '0',
        'description': 'documentation.',
        'author': 'Some Guy',
        'author_email': 'guy@example.com',
    }
    expected_extra = {
        'py_modules': ['test_module'],
    }

    package_files = ['test_module.py']

    handler = staticmethod(handle_setuptools)


class SetuptoolsNoSetupPyTest(unittest.TestCase, SetuptoolsTestCase):
    """
    Test handling a package without setup.py (only setup.cfg).
    """

    def make_package(self):
        d = super(SetuptoolsNoSetupPyTest, self).make_package()
        with open('setup.cfg', 'w') as f:
            f.write('\n'.join(['[metadata]'] +
                              ['{} = {}'.format(k, v) for k, v
                               in self.expected_base.items()] +
                              ['[options]'] +
                              ['{} = {}'.format(k, ', '.join(v)) for k, v
                               in self.expected_extra.items()]))
        return d

    def test_mocked(self):
        metadata = toml.loads(self.toml_base + self.toml_extra)
        with patch('setuptools.setup') as mock_setup:
            with self.make_package():
                self.handler(metadata)
                mock_setup.assert_called_with()


class SetuptoolsSetupPyTest(unittest.TestCase, SetuptoolsTestCase):
    """
    Test handling a packagewith setup.py.
    """

    def make_package(self):
        d = super(SetuptoolsSetupPyTest, self).make_package()
        with open('setup.py', 'w') as f:
            expected = dict(self.expected_base)
            expected.update(self.expected_extra)
            # the file is intentionally -x
            f.write('\n'.join(['from setuptools import setup',
                               'setup('] +
                              ['    {}={!r},'.format(k, v) for k, v
                               in expected.items()] +
                              ['    )']))
        return d

    def test_mocked(self):
        metadata = toml.loads(self.toml_base + self.toml_extra)
        with patch(
                'pyproject2setuppy.setuptools.subprocess.Popen') as mock_setup:
            mock_setup.return_value.wait = lambda: 0
            with self.make_package():
                self.handler(metadata)
                mock_setup.assert_called_with(
                    [sys.executable, 'setup.py'] + sys.argv[1:])
