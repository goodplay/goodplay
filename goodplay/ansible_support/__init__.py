# -*- coding: utf-8 -*-

import json
import os
import re
import sys

import py.path
import sarge
import yaml


def is_test_playbook_file(path):
    has_test_prefix = path.basename.startswith('test_')

    return has_test_prefix and is_playbook_file(path)


def is_playbook_file(path):
    is_yaml_file = path.ext == '.yml'

    if is_yaml_file:
        yaml_file_content = yaml.safe_load(path.read())
        yaml_file_is_ansible_playbook = \
            isinstance(yaml_file_content, list) \
            and len(yaml_file_content) \
            and isinstance(yaml_file_content[0], dict) \
            and (
                yaml_file_content[0].get('hosts')
                or yaml_file_content[0].get('include')
            )

        return yaml_file_is_ansible_playbook

    return False


class Playbook(object):
    tagged_tasks_re = re.compile(r'''
        ^\ {4}             # 4 spaces at the beginning of line
        (?:\ {2}TASK:\ )?  # additional task prefix used in ansible v2
        (?P<name>.*?)      # group: task name
        (?:\ {4}|\t)       # delimiter (spaces in ansible v2, tab in v1)
        TAGS:\ \[          # task tags prefix
        (?P<tags>.+?)      # group: task tags
        \]$                # task tags suffix at the end of line
        ''', re.VERBOSE)

    def __init__(self, playbook_path, inventory_path):
        self.playbook_path = playbook_path
        self.inventory_path = inventory_path

        # TODO: test for this playbook being contained in a role tests directory
        #       and provide role path to ansible
        self.installed_roles_path = py.path.local.mkdtemp()
        self.install_all_dependencies()

    @property
    def role_path(self):
        for ancestor_dir in self.playbook_path.parts(reverse=True)[1:]:
            if ancestor_dir.basename == 'tests':
                potential_role_path = ancestor_dir.dirpath()
                potential_meta_path = potential_role_path.join('meta', 'main.yml')

                if potential_meta_path.check(file=1):
                    return potential_role_path
                break

    def install_all_dependencies(self):
        self.install_role_dependencies()
        self.install_soft_dependencies()

    def install_role_dependencies(self):
        if not self.role_path:
            return

        role_meta_path = self.role_path.join('meta', 'main.yml')
        role_meta_content = yaml.safe_load(role_meta_path.read())
        role_dependencies = role_meta_content.get('dependencies', [])

        if role_dependencies:
            requirements_file = self.installed_roles_path.join('requirements')
            requirements_file.write('\n'.join(role_dependencies))

            cmd = sarge.shell_format(
                'ansible-galaxy install --force --role-file {0} --roles-path {1}',
                str(requirements_file),
                str(self.installed_roles_path))

            process = sarge.run(cmd, stdout=Capture(), stderr=Capture())
            print ''.join(process.stdout.readlines())
            if process.returncode != 0:
                raise Exception(process.stderr.readlines())

    def install_soft_dependencies(self):
        requirements_file = self.playbook_path.dirpath('requirements.yml')

        if requirements_file.check(file=1):
            cmd = sarge.shell_format(
                'ansible-galaxy install --force --role-file {0} --roles-path {1}',
                str(requirements_file),
                str(self.installed_roles_path))

            process = sarge.run(cmd, stdout=Capture(), stderr=Capture())
            print ''.join(process.stdout.readlines())
            if process.returncode != 0:
                raise Exception(process.stderr.readlines())

    def release(self):
        self.installed_roles_path.remove()

    def create_runner(self):
        return PlaybookRunner(self)

    def tasks(self, with_tag):
        roles_path = []
        if self.role_path:
            roles_path.append(str(self.role_path.dirpath()))
        roles_path.append(str(self.installed_roles_path))

        env = dict(
            ANSIBLE_ROLES_PATH=os.pathsep.join(roles_path),
        )

        cmd = sarge.shell_format(
            'ansible-playbook --list-tasks --list-tags -i {0} {1}',
            str(self.inventory_path),
            str(self.playbook_path))

        process = sarge.run(cmd, env=env, stdout=Capture(), stderr=Capture())
        if process.returncode != 0:
            raise Exception(process.stderr.readlines())

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


class PlaybookRunner(object):
    def __init__(self, playbook):
        self.playbook = playbook
        self.process = None
        self.skip_wait = False
        self.failures = []
        self.all_test_tasks_skipped = True

    def run_async(self):
        this_path = py.path.local(__file__)
        callback_plugin_path = this_path.dirpath('callback_plugin')

        roles_path = []
        if self.playbook.role_path:
            roles_path.append(str(self.playbook.role_path.dirpath()))
        roles_path.append(str(self.playbook.installed_roles_path))

        env = dict(
            PYTHONUNBUFFERED='1',
            ANSIBLE_CALLBACK_PLUGINS=str(callback_plugin_path),
            ANSIBLE_CALLBACK_WHITELIST='goodplay',
            ANSIBLE_ROLES_PATH=os.pathsep.join(roles_path),
        )

        cmd = sarge.shell_format(
            'ansible-playbook --verbose -i {0} {1}',
            self.playbook.inventory_path,
            self.playbook.playbook_path)

        self.process = sarge.run(cmd, env=env, stdout=Capture(), async=True)

        # wait for subprocess to be responsive
        self.process.wait_events()

    def wait(self):
        self.wait_for_event()

        for line in self.process.stdout:
            sys.stdout.write(line)

        self.process.wait()

        if self.all_test_tasks_skipped:
            self.failures.append('all test tasks have been skipped')

    def wait_for_event(self, event_name=None, **kwargs):
        for event in self.receive_events():
            if event['event_name'] == event_name:
                if all(item in event['data'].items()
                       for item in kwargs.items()):
                    return event
                else:  # pragma: no cover
                    message = 'found unexpected data in goodplay ' \
                        'event: {0!r}'.format(event)
                    raise Exception(message)
            elif event['event_name'] == 'error':
                error_message = event['data']['message']
                self.failures.append(error_message)
                self.skip_wait = True
                return
            else:  # pragma: no cover
                message = 'found unexpected goodplay event: {0!r}'.format(
                    event)
                raise Exception(message)

    def receive_events(self):
        event_line_prefix = 'GOODPLAY => '
        for line in self.process.stdout:
            sys.stdout.write(line)

            if line.startswith(event_line_prefix):
                event = json.loads(line[len(event_line_prefix):])
                yield event

    def wait_for_test_task(self, task):
        if self.skip_wait:
            return

        self.wait_for_event('test-task-start', name=task.name)

    def wait_for_test_task_outcome(self, task):
        if self.skip_wait:
            return

        event = self.wait_for_event('test-task-end', name=task.name)
        outcome = event['data']['outcome'] if event else 'skipped'

        if outcome != 'skipped':
            self.all_test_tasks_skipped = False

        return outcome
