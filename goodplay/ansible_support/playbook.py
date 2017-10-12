# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

import collections
import logging
import os
import re

import ansible.constants
from cached_property import cached_property
import yaml

from .runner import PlaybookRunner
from ..utils.subprocess import run

log = logging.getLogger(__name__)


class Playbook(object):
    tagged_tasks_re = re.compile(r'''
        (?:^\ {6})        # 6 spaces at the beginning of line
        (?P<name>.*?)     # group: task name
        (?:\t)            # 1 tab delimiter
        TAGS:\ \[         # task tags prefix
        (?P<tags>.+?)     # group: task tags
        \]$               # task tags suffix at the end of line
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
            log.info('role dependencies found in %s ... installing', role_meta_path)
            requirements_path = self.ctx.installed_roles_path.join('requirements.yml')
            requirements_path.write(yaml.dump(role_dependencies))

            self.install_roles_from_requirements_file(requirements_path)
        else:
            log.info('role dependencies not found in %s ... nothing to install',
                     role_meta_path)

    def install_soft_dependencies(self):
        requirements_path = self.ctx.playbook_path.dirpath('requirements.yml')

        if requirements_path.check(file=True):
            log.info('soft dependencies found in %s ... installing', requirements_path)
            self.install_roles_from_requirements_file(requirements_path)
        else:
            log.info('soft dependencies file not found at %s ... nothing to install',
                     requirements_path)

    def install_roles_from_requirements_file(self, requirements_file):
        ansible_galaxy_cmd = \
            'ansible-galaxy install -vvvv --force --role-file {0} --roles-path {1}'

        if self.ctx.use_local_roles:
            ansible_galaxy_cmd += ' --ignore-errors'

        process = run(ansible_galaxy_cmd, requirements_file, self.ctx.installed_roles_path)

        for line in process.stdout:
            log.info(line[:-1])

        if process.returncode != 0:
            raise Exception(process.stderr.readlines())  # pragma: no cover

    def env(self):
        roles_path = []

        if self.ctx.role_path:
            roles_path.append(self.ctx.role_under_test_roles_path.strpath)

        if self.ctx.use_local_roles:
            roles_path.extend(ansible.constants.DEFAULT_ROLES_PATH)

        roles_path.append(self.ctx.installed_roles_path.strpath)

        return dict(
            ANSIBLE_ROLES_PATH=os.pathsep.join(roles_path),
            ANSIBLE_RETRY_FILES_ENABLED='false',
            )

    def create_runner(self):
        return PlaybookRunner(self.ctx)

    @cached_property
    def test_tasks(self):
        test_tasks = [task for task in self.tasks() if 'test' in task.tags]
        self.ensure_unique_task_names(test_tasks)

        return test_tasks

    def ensure_unique_task_names(self, tasks):
        non_unique_task_names = [
            task_name for task_name, count in
            collections.Counter(task.name for task in tasks).items()
            if count > 1]

        if non_unique_task_names:
            raise ValueError(
                "Playbook '{0}' contains tests with non-unique name '{1}'"
                .format(self.ctx.playbook_path.strpath, non_unique_task_names[0]))

    def tasks(self):
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

                yield Task(name, tags)


class Task(object):
    def __init__(self, name, tags):
        self.name = name
        self.tags = tags
