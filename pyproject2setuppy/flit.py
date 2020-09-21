# pyproject2setup.py -- flit support
# vim:se fileencoding=utf-8 :
# (c) 2019-2020 Michał Górny
# 2-clause BSD license

from __future__ import absolute_import

from setuptools import setup

from collections import defaultdict

import importlib
import sys

from pyproject2setuppy.common import auto_find_packages


def handle_flit(data):
    """
    Handle pyproject.toml unserialized into data, using flit build
    system.
    """

    topdata = data['tool']['flit']
    metadata = topdata['metadata']
    modname = metadata['module']
    sys.path.insert(0, '.')
    mod = importlib.import_module(modname, '')

    entry_points = defaultdict(list)
    if 'scripts' in topdata:
        for name, content in topdata['scripts'].items():
            entry_points['console_scripts'].append(
                '{} = {}'.format(name, content)
            )

    if 'entrypoints' in topdata:
        for group_name, group_content in topdata['entrypoints'].items():
            for name, path in group_content.items():
                entry_points[group_name].append(
                    '{} = {}'.format(name, path)
                )

    package_args = auto_find_packages(modname)

    setup(name=modname,
          version=mod.__version__,
          description=mod.__doc__.strip(),
          author=metadata['author'],
          author_email=metadata['author-email'],
          url=metadata.get('home-page'),
          classifiers=metadata.get('classifiers', []),
          entry_points=dict(entry_points),
          # hack stolen from flit
          package_data={'': ['*']},
          **package_args)


def handle_flit_thyself(data):
    """Handle flit_core.build_thyself backend"""
    bs = data['build-system']
    sys.path.insert(0, bs['backend-path'])
    mod = importlib.import_module(bs['build-backend'], '')
    metadata = mod.metadata_dict
    package_args = auto_find_packages(bs['build-backend'].split('.')[0])

    setup(name=mod.metadata.name,
          version=mod.metadata.version,
          description=mod.metadata.summary,
          author=metadata['author'],
          author_email=metadata['author_email'],
          url=metadata.get('home_page'),
          classifiers=metadata.get('classifiers', []),
          **package_args)


def get_handlers():
    """
    Return build-backend mapping for flit.
    """

    return {'flit.buildapi': handle_flit,
            'flit_core.buildapi': handle_flit,
            'flit_core.build_thyself': handle_flit_thyself,
            }
