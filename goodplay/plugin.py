# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

import logging
import sys

from cached_property import cached_property
import pytest

from goodplay import ansible_support, docker_support, junitxml
from goodplay.context import GoodplayContext

junitxml.patch_pytest_to_strip_file_extensions()


# https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
logging.captureWarnings(True)


def enable_logging_goodplay_info_to_stdout():
    goodplay_stdout_handler = logging.StreamHandler(sys.stdout)
    goodplay_stdout_handler.setLevel(logging.INFO)
    goodplay_stdout_handler.setFormatter(logging.Formatter())

    goodplay_logger = logging.getLogger('goodplay')
    goodplay_logger.addHandler(goodplay_stdout_handler)
    goodplay_logger.setLevel(logging.DEBUG)


enable_logging_goodplay_info_to_stdout()


def pytest_addoption(parser):
    parser.getgroup('goodplay').addoption(
        '--use-local-roles', dest='use_local_roles', action='store_true',
        help='prefer to use local roles instead of auto-installed requirements')


class GoodplayFailed(Exception):
    pass


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if call.excinfo and call.excinfo.typename == 'GoodplayFailed':
        report.longrepr = 'Failed: {}'.format(call.excinfo.value)


# - GoodplayPlaybookFile (pytest.File)
#   - GoodplayEnvironment (pytest.Collector) -- manage Docker
#     - GoodplayPlaybook (pytest.Collector) -- manage Ansible runner
#       - GoodplayTest (pytest.Item)


def pytest_collect_file(parent, path):
    return GoodplayPlaybookFile.consider_and_create(path, parent)


class GoodplayContextSupport(object):
    @cached_property
    def ctx(self):
        return self.parent.ctx


# generic playbook preparations
class GoodplayPlaybookFile(pytest.File):
    def __init__(self, ctx, fspath, parent=None, config=None, session=None):
        super(GoodplayPlaybookFile, self).__init__(fspath, parent, config, session)

        self.ctx = ctx

    @classmethod
    def consider_and_create(cls, path, parent):
        if ansible_support.is_test_playbook_file(path):
            ctx = GoodplayContext(playbook_path=path, config=parent.config)

            if ctx.inventory_path:
                return GoodplayPlaybookFile(ctx, path, parent)

    def collect(self):
        try:
            environment_names = \
                docker_support.environment_names_for_playbook_path(self.ctx.playbook_path)

            if environment_names:
                for environment_name in environment_names:
                    yield GoodplayEnvironment(environment_name, self, self.config, self.session)
            else:
                yield GoodplayEnvironment(None, self, self.config, self.session)
        finally:
            if self.config.option.collectonly:
                self.ctx.release()

    def teardown(self):
        self.ctx.release()


# environment can be unspecific
class GoodplayEnvironment(GoodplayContextSupport, pytest.Collector):
    def __init__(self, environment_name, parent=None, config=None, session=None):
        if environment_name:
            # let the super class calculate the node id
            nodeid = None
        else:
            nodeid = parent.nodeid

        super(GoodplayEnvironment, self).__init__(
            environment_name, parent, config, session, nodeid=nodeid)
        self.environment_name = environment_name

        self.docker_runner = None

    def collect(self):
        yield GoodplayPlaybook(self.parent.name, self, self.config, self.session)

    def setup(self):
        self.docker_runner = docker_support.DockerRunner(self.ctx, self.environment_name)
        self.docker_runner.setup()

    def teardown(self):
        if self.docker_runner:
            self.docker_runner.teardown()


# environment specific playbook preparations
class GoodplayPlaybook(GoodplayContextSupport, pytest.Collector):
    def __init__(self, name, parent=None, config=None, session=None):
        super(GoodplayPlaybook, self).__init__(name, parent, config, session, nodeid=parent.nodeid)

        self.playbook_runner = None

    def collect(self):
        for task in self.ctx.playbook.test_tasks:
            yield GoodplayTest(task, self)

    def setup(self):
        self.playbook_runner = self.ctx.playbook.create_runner()
        self.playbook_runner.run_async()

    def teardown(self):
        if self.playbook_runner:
            self.playbook_runner.wait()

            if self.playbook_runner.failures:
                raise GoodplayFailed('\n'.join(self.playbook_runner.failures))


class GoodplayTest(GoodplayContextSupport, pytest.Item):
    def __init__(self, task, parent=None, config=None, session=None):
        super(GoodplayTest, self).__init__(task.name, parent, config, session)

        self.task = task

    def __repr__(self):
        return "<GoodplayTest '{0}'>".format(self.name)

    @cached_property
    def playbook_runner(self):
        return self.parent.playbook_runner

    def setup(self):
        self.playbook_runner.wait_for_test_task(self.task)

    def runtest(self):
        outcome = self.playbook_runner.wait_for_test_task_outcome(self.task)

        if outcome in ('skipped', None):
            pytest.skip()
        elif outcome == 'failed':
            raise GoodplayFailed()
