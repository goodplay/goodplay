# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

import logging
import os

log = logging.getLogger(__name__)


def pytest_collectstart(collector):
    is_root_collector = collector.parent is None
    if is_root_collector:
        testdir_path = collector.fspath
        if testdir_path.check(dir=False):
            testdir_path = testdir_path.join(os.pardir)

        log_testdir_content(testdir_path)


def log_testdir_content(testdir_path):
    for path in testdir_path.visit(fil=lambda x: x.check(dir=False), bf=True, sort=True):
        with path.open(mode='rb') as f:
            is_binary_file = is_binary_string(f.read(1024))

            if is_binary_file:
                log.info('## %s (binary file, content skipped)', testdir_path.bestrelpath(path))
            else:
                log.info('## %s\n%s', testdir_path.bestrelpath(path), path.read())


# based on file(1) behavior, see http://stackoverflow.com/a/7392391/5611889
TEXTCHARS = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})


def is_binary_string(_bytes):
    return bool(_bytes.translate(None, TEXTCHARS))
