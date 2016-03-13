# -*- coding: utf-8 -*-

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
            yield line

        # ensure remaining buffered lines are consumed (original code)
        while True:
            line = self.readline()
            if not line:
                break
            yield line
