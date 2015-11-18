# -*- coding: utf-8 -*-

from __future__ import print_function

import collections
import os
import re

from cached_property import cached_property
import yaml

from .runner import PlaybookRunner
from ..utils.subprocess import run


class Playbook(object):
    tagged_tasks_re = re.compile(r'''
        (?:^\ {6}TASK:\ )  # 6 spaces at the beginning of line plus task prefix
        (?P<name>.*?)      # group: task name
        (?:\ {4})          # 4 space delimiter
        TAGS:\ \[          # task tags prefix
        (?P<tags>.+?)      # group: task tags
        \]$                # task tags suffix at the end of line
        ''', re.VERBOSE)

    def __init__(self, ctx):
        self.ctx = ctx

        self.install_all_dependencies()

    def install_all_dependencies(self):
        self.install_role_dependencies()
        self.install_soft_dependencies()

    def install_role_dependencies(self):
        if not self.ctx.is_role_playbook:
            return

        role_meta_path = self.ctx.role_path.join('meta', 'main.yml')
        role_meta_content = yaml.safe_load(role_meta_path.read())
        role_dependencies = role_meta_content.get('dependencies', [])

        if role_dependencies:
            requirements_file = self.ctx.installed_roles_path.join('requirements.yml')
            requirements_file.write(yaml.dump(role_dependencies))

            self.install_roles_from_requirements_file(requirements_file)

    def install_soft_dependencies(self):
        requirements_file = self.ctx.playbook_path.dirpath('requirements.yml')

        if requirements_file.check(file=True):
            self.install_roles_from_requirements_file(requirements_file)

    def install_roles_from_requirements_file(self, requirements_file):
        process = run(
            'ansible-galaxy install -vvvv --force '
            '--role-file {0} --roles-path {1}',
            requirements_file, self.ctx.installed_roles_path)

        print(''.join(process.stdout.readlines()))
        if process.returncode != 0:
            raise Exception(process.stderr.readlines())  # pragma: no cover

    def env(self):
        roles_path = []
        if self.ctx.role_path:
            role_base_path = self.ctx.role_path.dirpath()
            roles_path.append(str(role_base_path))
        roles_path.append(str(self.ctx.installed_roles_path))

        return dict(ANSIBLE_ROLES_PATH=os.pathsep.join(roles_path))

    def create_runner(self):
        return PlaybookRunner(self.ctx)

    @cached_property
    def test_tasks(self):
        tasks = list(self.tasks(with_tag='test'))

        non_unique_task_names = [
            task_name for task_name, count in
            collections.Counter(task.name for task in tasks).items()
            if count > 1]

        if non_unique_task_names:
            raise ValueError(
                "Playbook '{0!s}' contains tests with non-unique name '{1}'"
                .format(self.ctx.playbook_path, non_unique_task_names[0]))

        return tasks

    def tasks(self, with_tag):
        __tracebackhide__ = True

        process = run(
            'ansible-playbook --list-tasks --list-tags -i {0} {1}',
            self.ctx.inventory_path, self.ctx.playbook_path,
            env=self.env())

        if process.returncode != 0:
            raise Exception(process.stderr.read())

        for line in process.stdout:
            match = self.tagged_tasks_re.match(line)

            if match:
                name = match.group('name')
                tags = [tag.strip() for tag in match.group('tags').split(',')]

                if with_tag in tags:
                    yield Task(name, tags)


class Task(object):
    def __init__(self, name, tags):
        self.name = name
        self.tags = tags
