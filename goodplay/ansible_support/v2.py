# -*- coding: utf-8 -*-

import ansible.parsing
import ansible.playbook
import ansible.vars

from goodplay.ansible_support.base import PlaybookRunner, Task


class Playbook(object):
    def __init__(self, playbook_path, inventory_path):
        self.playbook_path = playbook_path
        self.inventory_path = inventory_path

        self.passwords = {}
        self.loader = ansible.parsing.DataLoader()
        self.variable_manager = ansible.vars.VariableManager()

        self.playbook = self._build_playbook(playbook_path)

    def _build_playbook(self, playbook_path):
        return ansible.playbook.Playbook.load(
            file_name=str(playbook_path),
            variable_manager=self.variable_manager,
            loader=self.loader)

    def create_runner(self):
        return PlaybookRunner(self)

    def tasks(self, with_tag=None):
        for play in self.playbook.get_plays():
            for tasks in play.get_tasks():
                for task in tasks:
                    if with_tag is None or with_tag in task.tags:
                        yield Task(task)
