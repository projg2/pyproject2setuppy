# pyproject2setup.py -- setuptools support
# vim:se fileencoding=utf-8 :
# (c) 2020 Eli Schwartz
# 2-clause BSD license

from __future__ import absolute_import

import os
import subprocess
import sys


def handle_setuptools(data):
    """
    Handle pyproject.toml unserialized into data, by ignoring it and using the
    setuptools build system instead.

    Prefer running the contents of setup.py, but fall back to running a setup()
    function.
    """
    # TODO: shouldn't we be ignoring it with non-legacy backend?
    if os.path.exists('setup.py'):
        ret = (subprocess.Popen([sys.executable, 'setup.py'] + sys.argv[1:])
               .wait())
        if ret != 0:
            sys.exit(ret)
    else:
        from setuptools import setup
        setup()


def get_handlers():
    """
    Return build-backend mapping for setuptools.
    """

    return {'setuptools.build_meta': handle_setuptools,
            'setuptools.build_meta:__legacy__': handle_setuptools}
