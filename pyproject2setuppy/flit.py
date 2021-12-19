# pyproject2setup.py -- flit support
# vim:se fileencoding=utf-8 :
# (c) 2019-2021 Michał Górny
# 2-clause BSD license

from __future__ import absolute_import

from setuptools import setup

from collections import defaultdict

import importlib
import os.path
import sys

from pyproject2setuppy.common import auto_find_packages, find_package_data
from pyproject2setuppy.pep621 import get_pep621_metadata


def handle_flit(data):
    """
    Handle pyproject.toml unserialized into data, using flit build
    system.
    """

    # try PEP 621 first
    setup_metadata = get_pep621_metadata(data, ['version', 'description'])
    modname = None
    if setup_metadata is not None:
        if 'metadata' in data.get('tool', {}).get('flit', {}):
            raise ValueError('[project] and [tool.flit.metadata] cannot be '
                             'present simultaneously')

        # see if tool.flit.module specifies another module name
        modname = (data.get('tool', {}).get('flit', {})
                   .get('module', {}).get('name', None))
    else:
        # tool.flit fallback
        topdata = data['tool']['flit']
        metadata = topdata['metadata']

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

        setup_metadata = {
            'name': metadata['module'],
            # use None to match PEP 621 return value for dynamic
            'version': None,
            'description': None,
            'author': metadata['author'],
            'author_email': metadata['author-email'],
            'url': metadata.get('home-page'),
            'classifiers': metadata.get('classifiers', []),
            'entry_points': dict(entry_points),
        }

    # handle dynamic metadata if necessary
    if modname is None:
        modname = setup_metadata['name']

    if None in [setup_metadata[x] for x in ('version', 'description')]:
        sys.path.insert(0, '.')
        sys.path.insert(1, 'src')
        mod = importlib.import_module(modname.replace('/', '.'), '')
        if setup_metadata['version'] is None:
            setup_metadata['version'] = mod.__version__
        if setup_metadata['description'] is None:
            # setuptools doesn't like multiple lines in description
            setup_metadata['description'] = (
                ' '.join(mod.__doc__.strip().splitlines()))

    try:
        setup_metadata.update(auto_find_packages(modname))
    except RuntimeError:
        setup_metadata.update(auto_find_packages(modname, 'src'))
    setup_metadata['package_data'] = (
        find_package_data(setup_metadata.get('packages', []),
                          setup_metadata.get('package_dir', {})))

    setup(**setup_metadata)


def handle_flit_thyself(data):
    """Handle flit_core.build_thyself backend"""
    bs = data['build-system']
    backend_path = bs['backend-path']
    if not isinstance(backend_path, list):
        backend_path = [backend_path]
    sys.path = backend_path + sys.path
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
