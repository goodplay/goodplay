# -*- coding: utf-8 -*-

import pytest

from goodplay import ansible_support


def pytest_collect_file(parent, path):
    if ansible_support.is_test_playbook_file(path):
        return AnsiblePlaybook(path, parent)


class AnsiblePlaybook(pytest.File):
    @property
    def playbook_path(self):
        return self.fspath

    @property
    def inventory_path(self):
        inventory_path = self.playbook_path.dirpath('inventory')

        if inventory_path.check():
            return inventory_path

    def collect(self):
        if not self.inventory_path:
            return

        self.playbook = ansible_support.Playbook(
            self.playbook_path, self.inventory_path)

        try:
            already_seen_test_names = set()
            for task in self.playbook.tasks(with_tag='test'):
                test_name = task.name

                if test_name in already_seen_test_names:
                    raise ValueError(
                        '{0!r} contains tests with non-unique name {1!r}'.format(
                            self, str(test_name)))
                already_seen_test_names.add(test_name)

                yield AnsibleTestTask(task, self)
        finally:
            if self.config.option.collectonly:
                self.playbook.release()

    def setup(self):
        self.runner = self.playbook.create_runner()
        self.runner.run_async()

    def teardown(self):
        self.runner.wait()

        self.playbook.release()

        if self.runner.failures:
            pytest.fail('\n'.join(self.runner.failures))


class AnsibleTestTask(pytest.Item):
    def __init__(self, task, parent):
        super(AnsibleTestTask, self).__init__(task.name, parent)

        self.task = task

    @property
    def runner(self):
        return self.parent.runner

    def setup(self):
        self.runner.wait_for_test_task(self.task)

    def runtest(self):
        outcome = self.runner.wait_for_test_task_outcome(self.task)

        if outcome in ('skipped', None):
            pytest.skip()
        elif outcome == 'failed':
            pytest.fail()
