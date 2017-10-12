# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

import pytest

from goodplay.ansible_support import is_test_playbook_file


class CollectOnlyTestPlaybooks(object):
    def pytest_ignore_collect(self, path, config):
        # do not ignore directories
        if path.check(dir=True):
            return False

        # ignore everything else that is not a test playbook
        return not is_test_playbook_file(path)


def main():
    additional_plugins = [CollectOnlyTestPlaybooks()]

    raise SystemExit(pytest.main(plugins=additional_plugins))
