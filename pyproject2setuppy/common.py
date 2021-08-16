# pyproject2setup.py -- common routines
# vim:se fileencoding=utf-8 :
# (c) 2019-2020 Michał Górny
# 2-clause BSD license

from __future__ import absolute_import

from collections import defaultdict

from setuptools import find_packages

import os.path


def raise_exc(e):
    raise e


def auto_find_packages(modname, subdir='.'):
    """
    Find packages for modname, and supply proper setup() args for them.
    Supports both packages and modules in correct directory.  Includes
    all nested subpackages.
    """
    retdict = {}
    if subdir != '.':
        retdict['package_dir'] = {'': subdir}
    if os.path.isdir(os.path.join(subdir, modname)):
        retdict.update(
            {'packages': find_packages(where=subdir,
                                       include=(modname,
                                                '{}.*'.format(modname)))})
    elif os.path.isfile(os.path.join(subdir, modname + '.py')):
        retdict.update({'py_modules': [modname]})
    else:
        raise RuntimeError('No package matching {} found'.format(modname))
    return retdict


def find_package_data(packages, package_dirs={}):
    """Find additional package data dirs and return package_data dict."""
    ret = defaultdict(list)
    # install all data files from package directories
    ret[''] = ['*']

    # find data subdirectories
    for p in packages:
        pkgdir = package_dirs.get(p, os.path.join(package_dirs.get('', ''),
                                                  p.replace('.', '/')))
        for topdir, dirs, files in os.walk(pkgdir, onerror=raise_exc):
            dirs[:] = [x for x in dirs if x != '__pycache__'
                       and not x.startswith('.')]
            if '__init__.py' not in files:
                data_path = os.path.relpath(topdir, pkgdir)
                ret[p].append(data_path + '/*')

    return dict((x, sorted(frozenset(y))) for (x, y) in ret.items())
