# pyproject2setup.py -- main handler
# vim:se fileencoding=utf-8 :
# (c) 2019 Michał Górny
# 2-clause BSD license

import toml

import pyproject2setuppy.flit
import pyproject2setuppy.poetry


MODULES = (
    pyproject2setuppy.flit,
    pyproject2setuppy.poetry,
)


def get_handlers():
    handlers = {}
    for m in MODULES:
        handlers.update(m.get_handlers())
    return handlers


def main():
    with open('pyproject.toml') as f:
        data = toml.load(f)
    backend = data['build-system']['build-backend']

    handler = get_handlers().get(backend)
    if handler is None:
        raise NotImplementedError(
                'Build backend {} unknown'.format(backend))

    handler(data)
