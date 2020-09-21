# pyproject2setup.py -- poetry support
# vim:se fileencoding=utf-8 :
# (c) 2019-2020 Michał Górny
# 2-clause BSD license

from __future__ import absolute_import

from setuptools import find_packages, setup

from collections import defaultdict

import email.utils
import os.path

from pyproject2setuppy.common import auto_find_packages


def handle_poetry(data):
    """
    Handle pyproject.toml unserialized into data, using poetry build
    system.
    """

    metadata = data['tool']['poetry']

    authors = []
    author_emails = []
    for a in metadata['authors']:
        name, addr = email.utils.parseaddr(a)
        authors.append(name)
        author_emails.append(addr)

    if 'packages' not in metadata:
        package_args = auto_find_packages(metadata['name'])
    else:
        package_args = {'packages': [], 'package_dir': {}}
        for p in metadata['packages']:
            if p.get('format', '') == 'sdist':
                continue
            subdir = p.get('from', '.')
            packages = find_packages(
                subdir, include=(p['include'], p['include'] + '.*'))
            package_args['packages'].extend(packages)
            if subdir != '.':
                for sp in packages:
                    package_args['package_dir'][sp] = os.path.join(
                        subdir, sp.replace('.', os.path.sep))

    entry_points = defaultdict(list)
    if 'scripts' in metadata:
        for name, content in metadata['scripts'].items():
            entry_points['console_scripts'].append(
                '{} = {}'.format(name, content)
            )

    if 'plugins' in metadata:
        for group_name, group_content in metadata['plugins'].items():
            for name, path in group_content.items():
                entry_points[group_name].append(
                    '{} = {}'.format(name, path)
                )

    setup(name=metadata['name'],
          version=metadata['version'],
          description=metadata['description'],
          author=', '.join(authors),
          author_email=', '.join(author_emails),
          url=metadata.get('homepage'),
          classifiers=metadata.get('classifiers', []),
          entry_points=dict(entry_points),
          # hack stolen from flit
          package_data={'': ['*']},
          **package_args)


def get_handlers():
    """
    Return build-backend mapping for poetry.
    """

    return {'poetry.masonry.api': handle_poetry}
