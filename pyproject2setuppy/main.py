# pyproject2setup.py -- backwards compatibility for .main module
# vim:se fileencoding=utf-8 :
# (c) 2021 Michał Górny
# 2-clause BSD license

from __future__ import absolute_import

from pyproject2setuppy.__main__ import get_handlers, main


__all__ = [get_handlers, main]


if __name__ == '__main__':
    main()
