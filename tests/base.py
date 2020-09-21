# vim:se fileencoding=utf-8 :
# (c) 2019 Michał Górny
# 2-clause BSD license

import importlib
import os
import os.path
import sys
import toml
import zipfile

from distutils.sysconfig import get_python_lib
from distutils.util import change_root

if sys.hexversion >= 0x03000000:
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
else:
    from backports.tempfile import TemporaryDirectory
    from mock import patch


def find_all_pkg_files(topdir):
    """
    Find all package files in the directory tree starting with topdir,
    and yield their relative paths.
    """

    for dirpath, dirs, files in os.walk(topdir, topdown=True):
        for d in list(dirs):
            if d.endswith('.egg-info') or d == '__pycache__':
                dirs.remove(d)
        for f in files:
            if not (f.endswith('.pyc') or f.endswith('.pyo')):
                yield os.path.relpath(os.path.join(dirpath, f), topdir)


def find_eggs(sitedir):
    """
    Find all .egg-info directories in sitedir, and return their names.
    """

    for _, dirs, _ in os.walk(sitedir):
        for d in dirs:
            if d.endswith('.egg-info'):
                yield d
        break


def zip_find_distinfos(files):
    """
    Find all .dist-info directories from zip namelist() passed as files.
    """

    for f in files:
        head, tail = os.path.split(f)
        if head.endswith('.dist-info'):
            yield head


class TestDirectory(object):
    """
    A thin wrapper over TemporaryDirectory, entering it and leaving
    via context manager.
    """

    def __init__(self):
        self.tempdir = TemporaryDirectory()
        self.saved_cwd = os.getcwd()
        os.chdir(self.tempdir.name)

    def __enter__(self):
        return self.tempdir.__enter__()

    def __exit__(self, *args):
        os.chdir(self.saved_cwd)
        return self.tempdir.__exit__(*args)


class BuildSystemTestCase(object):
    """
    Base test case for a build system.
    """

    @property
    def toml_base(self):
        """
        TOML contents as string, defined in the base build system class.
        """
        return ''

    @property
    def toml_extra(self):
        """
        TOML contents as string, defined in the specific test case.
        """
        return ''

    @property
    def expected_base(self):
        """
        Expected setup() arguments as dict, defined in the base build
        system class.
        """
        return {}

    @property
    def expected_extra(self):
        """
        Expected setup() arguments as dict, defined in the specifc test
        case.
        """
        return {}

    @property
    def expected_extra_files(self):
        """
        Additional files expected installed as part of the package.
        """
        return []

    @property
    def package_files(self):
        """
        List of (empty) files to be created in the package directory.
        """
        return []

    @property
    def handler(self):
        """
        Tested handler function.
        """
        return None

    def make_expected(self, args):
        """
        Make a list of expected .py files based on expected setuptools args.
        """

        for p in args.get('py_modules', []):
            yield p + '.py'
        for p in args.get('packages', []):
            yield os.path.join(p.replace('.', os.path.sep), '__init__.py')
        for f in self.expected_extra_files:
            yield f

    def make_package(self):
        """
        Make a temporary directory and write tested package files in it.
        Returns TemporaryDirectory instance (to be used as context
        manager).
        """

        d = TestDirectory()
        for fn in self.package_files:
            dn = os.path.dirname(fn)
            if dn and not os.path.isdir(dn):
                os.makedirs(dn)
            with open(fn, 'w'):
                pass
        return d

    def test_mocked(self):
        """
        Test the handler with mocked setup().  Verifies that correct
        arguments are passed.
        """

        metadata = toml.loads(self.toml_base + self.toml_extra)
        with patch(self.handler.__module__ + '.setup') as mock_setup:
            with self.make_package():
                self.handler(metadata)
                expected = self.expected_base.copy()
                expected.update(self.expected_extra)
                mock_setup.assert_called_with(**expected)

    def test_build(self):
        """
        Test the handler with 'setup.py build' command.  Verifies that
        correct .py files are built.
        """

        metadata = toml.loads(self.toml_base + self.toml_extra)
        sys.argv = ['setup.py', 'build', '--build-lib', 'build/lib']
        with self.make_package() as d:
            self.handler(metadata)
            expected = self.expected_base.copy()
            expected.update(self.expected_extra)
            build_dir = os.path.join(d, 'build', 'lib')
            self.assertEqual(sorted(find_all_pkg_files(build_dir)),
                             sorted(self.make_expected(expected)))

    def test_install(self):
        """
        Test the handler with 'setup.py install' command.  Verifies that
        correct .py files and .egg-info directory are installed.
        """

        metadata = toml.loads(self.toml_base + self.toml_extra)
        with TemporaryDirectory() as dest:
            sys.argv = ['setup.py', 'install', '--root=' + dest]
            with self.make_package():
                self.handler(metadata)
                expected = self.expected_base.copy()
                expected.update(self.expected_extra)
                inst_dir = change_root(dest, get_python_lib())
                self.assertEqual(sorted(find_all_pkg_files(inst_dir)),
                                 sorted(self.make_expected(expected)))
                tag = 'py{}.{}.egg-info'.format(*sys.version_info[:2])
                eggname = '-'.join((expected['name'],
                                    expected['version'],
                                    tag))
                self.assertEqual(sorted(find_eggs(inst_dir)), [eggname])

    def test_real_build_system(self):
        """
        Perform a self-test using the upstream build backend.  Builds
        a wheel, and verifies its contents.  Used to verify that test
        cases are correct.
        """

        metadata = toml.loads(self.toml_base + self.toml_extra)
        backend_module = metadata['build-system']['build-backend']
        try:
            backend = importlib.import_module(backend_module)
        except ImportError:
            self.skipTest('Required {} module missing'.format(backend_module))

        with self.make_package() as d:
            with open('pyproject.toml', 'w') as f:
                f.write(self.toml_base + self.toml_extra)

            whl = backend.build_wheel(d)
            with zipfile.ZipFile(whl) as zf:
                expected = self.expected_base.copy()
                expected.update(self.expected_extra)
                pkg_files = [x for x in zf.namelist()
                             if not x.split('/')[0].endswith('.dist-info')]
                self.assertEqual(sorted(pkg_files),
                                 sorted(self.make_expected(expected)))
                distinfos = frozenset(zip_find_distinfos(zf.namelist()))
                distname = '{}-{}.dist-info'.format(expected['name'],
                                                    expected['version'])
                self.assertEqual(sorted(distinfos),
                                 sorted([distname]))
