# pyproject2setup.py -- poetry support
# vim:se fileencoding=utf-8 :
# (c) 2019 Michał Górny
# 2-clause BSD license

from setuptools import setup

import email.utils

from pyproject2setuppy.common import auto_find_packages


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


def get_handlers():
    return {'poetry.masonry.api': handle_poetry}
