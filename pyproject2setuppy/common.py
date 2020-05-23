# pyproject2setup.py -- common routines
# vim:se fileencoding=utf-8 :
# (c) 2019-2020 Michał Górny
# 2-clause BSD license

from __future__ import absolute_import

from setuptools import find_packages

import os.path


def auto_find_packages(modname):
    """
    Find packages for modname, and supply proper setup() args for them.
    Supports both packages and modules in correct directory.  Includes
    all nested subpackages.
    """
    if os.path.isdir(modname):
        return {'packages': find_packages(include=(modname,
                                                   '{}.*'.format(modname)))}
    else:
        return {'py_modules': [modname]}
