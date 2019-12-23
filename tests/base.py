# vim:se fileencoding=utf-8 :
# (c) 2019 Michał Górny
# 2-clause BSD license

import os
import os.path
import sys
import toml

if sys.hexversion >= 0x03000000:
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
else:
    from backports.tempfile import TemporaryDirectory
    from mock import patch


class BuildSystemTestCase(object):
    toml_base = ''
    toml_extra = ''

    expected_base = {}
    expected_extra = {}

    package_files = []

    module = ''
    handler = None

    def make_package(self):
        d = TemporaryDirectory()
        os.chdir(d.name)
        for fn in self.package_files:
            dn = os.path.dirname(fn)
            if dn:
                os.makedirs(dn)
            with open(fn, 'w'):
                pass
        return d

    def test_mocked(self):
        metadata = toml.loads(self.toml_base + self.toml_extra)
        with patch(self.module + '.setup') as mock_setup:
            with self.make_package():
                self.handler(metadata)
                expected = self.expected_base.copy()
                expected.update(self.expected_extra)
                mock_setup.assert_called_with(**expected)
