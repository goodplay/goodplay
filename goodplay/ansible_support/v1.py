# -*- coding: utf-8 -*-

import ansible
import ansible.inventory
import ansible.playbook

from goodplay.ansible_support.base import PlaybookRunner, Task


class Playbook(object):
    def __init__(self, playbook_path, inventory_path):
        self.playbook_path = playbook_path
        self.inventory_path = inventory_path

        self.inventory = self._build_inventory(inventory_path)
        self.playbook = self._build_playbook(self.inventory, playbook_path)

    def _build_inventory(self, inventory_path):
        return ansible.inventory.Inventory(str(inventory_path))

    def _build_playbook(self, inventory, playbook_path):
        stats = ansible.callbacks.AggregateStats()
        runner_callbacks = ansible.callbacks.PlaybookRunnerCallbacks(stats)
        callbacks = ansible.callbacks.PlaybookCallbacks()

        return ansible.playbook.PlayBook(
            inventory=inventory,
            playbook=str(playbook_path),
            callbacks=callbacks,
            runner_callbacks=runner_callbacks,
            stats=stats,
        )

    def create_runner(self):
        return PlaybookRunner(self)

    def tasks(self, with_tag=None):
        for play_ds, play_basedir in zip(
                self.playbook.playbook, self.playbook.play_basedirs):
            play = ansible.playbook.Play(self.playbook, play_ds, play_basedir)
            for task in self.playbook.tasks_to_run_in_play(play):
                if getattr(task, 'name', None) is None:
                    continue

                if with_tag is None or with_tag in task.tags:
                    yield Task(task)
