# pyproject2setup.py -- flit support
# vim:se fileencoding=utf-8 :
# (c) 2019-2020 Michał Górny
# 2-clause BSD license

from __future__ import absolute_import

from setuptools import setup

import importlib
import sys

from pyproject2setuppy.common import auto_find_packages


def handle_flit(data):
    """
    Handle pyproject.toml unserialized into data, using flit build
    system.
    """

    metadata = data['tool']['flit']['metadata']
    modname = metadata['module']
    sys.path.insert(0, '.')
    mod = importlib.import_module(modname, '')

    if 'scripts' in data['tool']['flit']:
        raise NotImplementedError('flit.scripts not supported yet')
    if 'entrypoints' in data['tool']['flit']:
        raise NotImplementedError('flit.entrypoints not supported yet')

    package_args = auto_find_packages(modname)

    setup(name=modname,
          version=mod.__version__,
          description=mod.__doc__.strip(),
          author=metadata['author'],
          author_email=metadata['author-email'],
          url=metadata.get('home-page'),
          classifiers=metadata.get('classifiers', []),
          **package_args)


def get_handlers():
    """
    Return build-backend mapping for flit.
    """

    return {'flit.buildapi': handle_flit,
            'flit_core.buildapi': handle_flit,
            }
