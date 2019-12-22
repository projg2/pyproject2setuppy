# pyproject2setup.py -- common routines
# vim:se fileencoding=utf-8 :
# (c) 2019 Michał Górny
# 2-clause BSD license

from setuptools import find_packages

import os.path


def auto_find_packages(modname):
    """
    Find packages for modname, and supply proper setup() args for them.
    Supports both packages and modules in correct directory.
    """
    if os.path.isdir(modname):
        return {'packages': find_packages(include=(modname,
                                                   '{}.*'.format(modname)))}
    else:
        return {'py_modules': [modname]}
