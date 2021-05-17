# pyproject2setup.py -- PEP 621 metadata support
# vim:se fileencoding=utf-8 :
# (c) 2021 Michał Górny
# 2-clause BSD license

from collections import defaultdict


def get_pep621_metadata(data, allow_dynamic=[]):
    """
    Get PEP 621 metadata if available, return None otherwise.
    """

    if 'project' not in data:
        return None
    metadata = data['project']

    # TODO: follow PEP621 author/email split?
    authors = []
    author_emails = []
    for a in metadata['authors']:
        if 'name' in a:
            authors.append(a['name'])
        if 'email' in a:
            author_emails.append(a['email'])

    entry_points = defaultdict(list)
    if 'scripts' in metadata:
        for name, content in metadata['scripts'].items():
            entry_points['console_scripts'].append(
                '{} = {}'.format(name, content)
            )

    if 'gui-scripts' in metadata:
        for name, content in metadata['gui-scripts'].items():
            entry_points['gui_scripts'].append(
                '{} = {}'.format(name, content)
            )

    if 'entrypoints' in metadata:
        for group_name, group_content in metadata['entrypoints'].items():
            if group_name in ('console_scripts', 'gui_scripts'):
                raise ValueError('{} forbidden in entrypoints'
                                 .format(group_name))
            for name, path in group_content.items():
                entry_points[group_name].append(
                    '{} = {}'.format(name, path)
                )

    for key in allow_dynamic:
        has_static = key in metadata
        has_dynamic = key in metadata.get('dynamic', [])
        if has_static and has_dynamic:
            raise ValueError('Key {} declared both statically and as dynamic'
                             .format(key))
        if not has_static and not has_dynamic:
            raise ValueError('Key {} must be declared either statically or as '
                             'dynamic'.format(key))

    return {
        'name': metadata['name'],
        'version': metadata.get('version'),
        'description': metadata.get('description'),
        'author': ', '.join(authors),
        'author_email': ', '.join(author_emails),
        'classifiers': metadata.get('classifiers', []),
        'entry_points': dict(entry_points),
    }
