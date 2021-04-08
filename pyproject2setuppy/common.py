# pyproject2setup.py -- common routines
# vim:se fileencoding=utf-8 :
# (c) 2019-2020 Michał Górny
# 2-clause BSD license

from __future__ import absolute_import

from setuptools import find_packages

import os.path


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
