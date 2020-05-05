# pyproject2setup.py -- main handler
# vim:se fileencoding=utf-8 :
# (c) 2019-2020 Michał Górny
# 2-clause BSD license

from __future__ import absolute_import

import toml

import pyproject2setuppy.flit
import pyproject2setuppy.poetry
import pyproject2setuppy.setuptools


MODULES = (
    pyproject2setuppy.flit,
    pyproject2setuppy.poetry,
    pyproject2setuppy.setuptools,
)


def get_handlers():
    """
    Get mapping of build-backend values for supported build systems.
    """

    handlers = {}
    for m in MODULES:
        handlers.update(m.get_handlers())
    return handlers


def main():
    """
    Run setuptools' setup() function for pyproject.toml in the current
    working directory.
    """

    with open('pyproject.toml') as f:
        data = toml.load(f)
    backend = data['build-system']['build-backend']

    handler = get_handlers().get(backend)
    if handler is None:
        raise NotImplementedError(
                'Build backend {} unknown'.format(backend))

    handler(data)


if __name__ == '__main__':
    main()
