# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

import logging
import json

import py.path

from ..utils.subprocess import run

log = logging.getLogger(__name__)


class PlaybookRunner(object):
    def __init__(self, ctx):
        self.ctx = ctx

        self.process = None
        self.skip_wait = False
        self.failures = []
        self.all_test_tasks_skipped = True

    def run_async(self):
        this_path = py.path.local(__file__)
        callback_plugin_path = this_path.dirpath('callback_plugin')
        connection_plugin_path = this_path.dirpath('connection_plugin')

        env = self.ctx.playbook.env()
        additional_env = dict(
            PYTHONUNBUFFERED='1',
            ANSIBLE_CALLBACK_PLUGINS=callback_plugin_path.strpath,
            ANSIBLE_CALLBACK_WHITELIST='goodplay',
            ANSIBLE_CONNECTION_PLUGINS=connection_plugin_path.strpath,
        )
        env.update(additional_env)

        self.process = run(
            'ansible-playbook -vvv -i {0} {1}',
            self.ctx.extended_inventory_path, self.ctx.playbook_path,
            env=env, async_=True)

        # wait for subprocess to be responsive
        self.process.wait_events()

    def wait(self):
        self.wait_for_event()

        for line in self.process.stdout:
            log.info(line[:-1])

        self.process.wait()

        if self.all_test_tasks_skipped:
            self.failures.append('all test tasks have been skipped')

    def wait_for_event(self, event_name=None, **kwargs):
        for event in self.receive_events():
            if event['event_name'] == event_name \
                    and set(kwargs.items()).issubset(set(event['data'].items())):
                return event
            elif event['event_name'] == 'error':
                error_message = event['data']['message']
                self.failures.append(error_message)
                self.skip_wait = True
                return
            else:  # pragma: no cover
                raise Exception('found unexpected goodplay event: {0!r}'.format(event))

    def receive_events(self):
        event_line_prefix = 'GOODPLAY => '
        for line in self.process.stdout:
            log.info(line[:-1])

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
