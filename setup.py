#!/usr/bin/env python
# pyproject2setup.py -- cheap builder for pyproject-based build systems
# vim:se fileencoding=utf-8 :
# (c) 2019 Michał Górny
# 2-clause BSD license

from setuptools import find_packages, setup
import email.utils
import importlib
import os.path
import sys
import toml


def auto_find_packages(modname):
    """
    Find packages for modname, and supply proper setup() args for them.
    Supports both packages and modules in correct directory.
    """
    if os.path.isdir(modname):
        return {'packages': find_packages(include=(modname,
                                                   '{}.*'.format(modname)))}
    else:
        return {'py_modules': (modname,)}


def handle_flit(data):
    metadata = data['tool']['flit']['metadata']
    modname = metadata['module']
    sys.path.insert(0, '.')
    mod = importlib.import_module(modname, '')

    if 'scripts' in data['tool']['flit']:
        raise NotImplementedError('flit.scripts not supported yet')

    package_args = auto_find_packages(modname)

    setup(name=modname,
          version=mod.__version__,
          description=mod.__doc__,
          author=metadata['author'],
          author_email=metadata['author-email'],
          url=metadata.get('home-page'),
          classifiers=metadata.get('classifiers', []),
          **package_args)


def handle_poetry(data):
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
        package_args = {'packages': []}
        for p in metadata['packages']:
            if p.get('format', '') == 'sdist':
                continue
            package_args['packages'].extend(find_packages(
                include=(p['include'],)))

    setup(name=metadata['name'],
          version=metadata['version'],
          description=metadata['description'],
          author=', '.join(authors),
          author_email=', '.join(author_emails),
          url=metadata.get('homepage'),
          classifiers=metadata.get('classifiers', []),
          **package_args)


def main():
    with open('pyproject.toml') as f:
        data = toml.load(f)

    backend = data['build-system']['build-backend']
    if backend == 'flit.buildapi':
        handle_flit(data)
    elif backend == 'poetry.masonry.api':
        handle_poetry(data)
    else:
        raise NotImplementedError(
                'Build backend {} unknown'.format(backend))


if __name__ == '__main__':
    main()
