# pyproject2setup.py -- setuptools support
# vim:se fileencoding=utf-8 :
# (c) 2020 Eli Schwartz
# 2-clause BSD license

from __future__ import absolute_import

import os
import sys


def handle_setuptools(data):
    """
    Handle pyproject.toml unserialized into data, by ignoring it and using the
    setuptools build system instead.

    Prefer running the contents of setup.py, but fall back to running a setup()
    function.
    """
    if os.path.exists('setup.py'):
        os.execv(
            sys.executable,
            ['pyproject2setuppy', 'setup.py'] + sys.argv[1:])
    else:
        from setuptools import setup
        setup()


def get_handlers():
    """
    Return build-backend mapping for setuptools.
    """

    return {'setuptools.build_meta': handle_setuptools}
