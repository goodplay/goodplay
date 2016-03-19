# -*- coding: utf-8 -*-

import re

import _pytest.junitxml


def patch_pytest_to_strip_file_extensions():
    if hasattr(_pytest.junitxml, '_py_ext_re'):
        # pytest>=2.9.1
        _pytest.junitxml._py_ext_re = re.compile(r'\.(?:py|yml)$')
    else:  # pragma: no cover
        # pytest<=2.9.0
        # monkeypatch mangle_testnames to remove .yml extension from playbook "class"
        mangle_testnames_orig = _pytest.junitxml.mangle_testnames

        def mangle_testnames_patch(names):
            names = mangle_testnames_orig(names)
            return [x[:-4] if x.endswith('.yml') else x for x in names[:-1]] + [names[-1]]
        _pytest.junitxml.mangle_testnames = mangle_testnames_patch
