# -*- coding: utf-8 -*-

import json
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

    def create_runner(self):
        return PlaybookRunner(self)

    def tasks(self, with_tag):
        env = dict(PYTHONUNBUFFERED='1')
        cmd = sarge.shell_format(
            'ansible-playbook --list-tasks --list-tags -i {0} {1}',
            str(self.inventory_path),
            str(self.playbook_path))

        process = sarge.run(cmd, env=env, stdout=Capture())

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

        env = dict(
            PYTHONUNBUFFERED='1',
            ANSIBLE_CALLBACK_PLUGINS=str(callback_plugin_path),
            ANSIBLE_CALLBACK_WHITELIST='goodplay')

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
