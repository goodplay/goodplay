# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

import logging
import sarge

log = logging.getLogger(__name__)


def run(command, *args, **kwargs):
    command = sarge.shell_format(command, *args)
    log.info('run process: %s', command)

    return sarge.run(command, stdout=Capture(), stderr=Capture(), **kwargs)


class Capture(sarge.Capture):
    def __iter__(self):
        # override default Capture to read lines as long as streams are open,
        # thus iteration is not being stopped by large pauses between lines
        # being available
        while self.streams_open():
            line = self.readline()
            if not line:
                continue
            yield line.decode('utf-8')

        # ensure remaining buffered lines are consumed (original code)
        while True:
            line = self.readline()
            if not line:
                break
            yield line.decode('utf-8')
