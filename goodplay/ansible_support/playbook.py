# -*- coding: utf-8 -*-

import re

from .dependency import DependencySupport
from .role import RoleSupport
from .runner import PlaybookRunner
from ..utils.subprocess import run


class Playbook(RoleSupport, DependencySupport):
    tagged_tasks_re = re.compile(r'''
        (?:^\ {6}TASK:\ )  # 6 spaces at the beginning of line plus task prefix
        (?P<name>.*?)      # group: task name
        (?:\ {4})          # 4 space delimiter
        TAGS:\ \[          # task tags prefix
        (?P<tags>.+?)      # group: task tags
        \]$                # task tags suffix at the end of line
        ''', re.VERBOSE)

    def __init__(self, playbook_path, inventory_path):
        self.playbook_path = playbook_path
        self.inventory_path = inventory_path

        DependencySupport.initialize(self)

    def release(self):
        DependencySupport.release(self)

    def env(self):
        return DependencySupport.env(self)

    def create_runner(self):
        return PlaybookRunner(self)

    def tasks(self, with_tag):
        __tracebackhide__ = True

        process = run(
            'ansible-playbook --list-tasks --list-tags -i {0} {1}',
            self.inventory_path, self.playbook_path,
            env=self.env())

        if process.returncode != 0:
            raise Exception(process.stderr.read())

        for line in process.stdout:
            match = self.tagged_tasks_re.match(line)

            if match:
                name = match.group('name')
                tags = (tag.strip() for tag in match.group('tags').split(','))

                if with_tag in tags:
                    yield Task(name, tags)


class Task(object):
    def __init__(self, name, tags):
        self.name = name
        self.tags = tags
