# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

import re

import _pytest.junitxml


def patch_pytest_to_strip_file_extensions():
    _pytest.junitxml._py_ext_re = re.compile(r'\.(?:py|yml)$')
