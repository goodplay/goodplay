# -*- coding: utf-8 -*-

import logging

from cached_property import cached_property
import pytest

from goodplay import ansible_support, docker_support, junitxml
from goodplay.context import GoodplayContext

# https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning
logging.captureWarnings(True)

junitxml.patch_mangle_testnames()


def pytest_addoption(parser):
    group = parser.getgroup('goodplay')
    group.addoption(
        '--use-local-roles', action='store_true',
        help='some help text')


# - GoodplayPlaybookFile (pytest.File)
#   - GoodplayPlatform (pytest.Collector) -- manage docker
#     - GoodplayPlaybook (pytest.Collector) -- manage ansible runner
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
            ctx = GoodplayContext(playbook_path=path, pytestconfig=parent.config)

            if ctx.inventory_path:
                return GoodplayPlaybookFile(ctx, path, parent)

    def collect(self):
        try:
            platforms = self.ctx.platforms if self.ctx.platforms else (None,)

            for platform in platforms:
                yield GoodplayPlatform(platform, self, self.config, self.session)
        finally:
            if self.config.option.collectonly:
                self.ctx.release()

    def teardown(self):
        self.ctx.release()


# platform can be unspecific
class GoodplayPlatform(GoodplayContextSupport, pytest.Collector):
    def __init__(self, platform, parent=None, config=None, session=None):
        super(GoodplayPlatform, self).__init__(str(platform), parent, config, session)
        self.platform = platform

        self.docker_runner = None

    def _makeid(self):
        if not self.platform:
            return self.parent.nodeid

        return super(GoodplayPlatform, self)._makeid()

    def collect(self):
        yield GoodplayPlaybook(self.parent.name, self, self.config, self.session)

    def setup(self):
        self.docker_runner = docker_support.DockerRunner(self.ctx, self.platform)
        self.docker_runner.setup()

    def teardown(self):
        if self.docker_runner:
            self.docker_runner.teardown()


# platform specific playbook preparations
class GoodplayPlaybook(GoodplayContextSupport, pytest.Collector):
    def __init__(self, name, parent=None, config=None, session=None):
        super(GoodplayPlaybook, self).__init__(name, parent, config, session)

        self.playbook_runner = None

    def _makeid(self):
        return self.parent.nodeid

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
                pytest.fail('\n'.join(self.playbook_runner.failures))


class GoodplayTest(GoodplayContextSupport, pytest.Item):
    def __init__(self, task, parent=None, config=None, session=None):
        super(GoodplayTest, self).__init__(task.name, parent, config, session)

        self.task = task

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
            pytest.fail()
