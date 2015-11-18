# -*- coding: utf-8 -*-

import _pytest.junitxml


def patch_mangle_testnames():
    # monkeypatch mangle_testnames to remove .yml extension from playbook "class"
    mangle_testnames_orig = _pytest.junitxml.mangle_testnames

    def mangle_testnames_patch(names):
        names = mangle_testnames_orig(names)
        return [x[:-4] if x.endswith('.yml') else x for x in names[:-1]] + [names[-1]]
    _pytest.junitxml.mangle_testnames = mangle_testnames_patch
