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


def find_all_py(topdir):
    for dirpath, dirs, files in os.walk(topdir):
        for f in files:
            if f.endswith('.py'):
                yield os.path.relpath(os.path.join(dirpath, f), topdir)


def find_eggs(sitedir):
    for _, dirs, _ in os.walk(sitedir):
        for d in dirs:
            if d.endswith('.egg-info'):
                yield d
        break


def zip_find_distinfos(files):
    for f in files:
        head, tail = os.path.split(f)
        if head.endswith('.dist-info'):
            yield head


def make_expected(args):
    for p in args.get('py_modules', []):
        yield p + '.py'
    for p in args.get('packages', []):
        yield os.path.join(p.replace('.', os.path.sep), '__init__.py')


class BuildSystemTestCase(object):
    toml_base = ''
    toml_extra = ''

    expected_base = {}
    expected_extra = {}

    package_files = []

    module = ''
    handler = None

    def make_package(self):
        d = TemporaryDirectory()
        os.chdir(d.name)
        for fn in self.package_files:
            dn = os.path.dirname(fn)
            if dn:
                os.makedirs(dn)
            with open(fn, 'w'):
                pass
        return d

    def test_mocked(self):
        metadata = toml.loads(self.toml_base + self.toml_extra)
        with patch(self.module + '.setup') as mock_setup:
            with self.make_package():
                self.handler(metadata)
                expected = self.expected_base.copy()
                expected.update(self.expected_extra)
                mock_setup.assert_called_with(**expected)

    def test_build(self):
        metadata = toml.loads(self.toml_base + self.toml_extra)
        sys.argv = ['setup.py', 'build']
        with self.make_package() as d:
            self.handler(metadata)
            expected = self.expected_base.copy()
            expected.update(self.expected_extra)
            build_dir = os.path.join(d, 'build', 'lib')
            self.assertEqual(sorted(find_all_py(build_dir)),
                             sorted(make_expected(expected)))

    def test_install(self):
        metadata = toml.loads(self.toml_base + self.toml_extra)
        with TemporaryDirectory() as dest:
            sys.argv = ['setup.py', 'install', '--root=' + dest]
            with self.make_package():
                self.handler(metadata)
                expected = self.expected_base.copy()
                expected.update(self.expected_extra)
                inst_dir = change_root(dest, get_python_lib())
                self.assertEqual(sorted(find_all_py(inst_dir)),
                                 sorted(make_expected(expected)))
                tag = 'py{}.{}.egg-info'.format(*sys.version_info[:2])
                eggname = '-'.join((expected['name'],
                                    expected['version'],
                                    tag))
                self.assertEqual(sorted(find_eggs(inst_dir)), [eggname])

    def test_real_build_system(self):
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
                pyfiles = [x for x in zf.namelist() if x.endswith('.py')]
                self.assertEqual(sorted(pyfiles),
                                 sorted(make_expected(expected)))
                distinfos = frozenset(zip_find_distinfos(zf.namelist()))
                distname = '{}-{}.dist-info'.format(expected['name'],
                                                    expected['version'])
                self.assertEqual(sorted(distinfos),
                                 sorted([distname]))
