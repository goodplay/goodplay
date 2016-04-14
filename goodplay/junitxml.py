# -*- coding: utf-8 -*-

import re

import _pytest.junitxml


def patch_pytest_to_strip_file_extensions():
    _pytest.junitxml._py_ext_re = re.compile(r'\.(?:py|yml)$')
