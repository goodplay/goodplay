# -*- coding: utf-8 -*-

import json
import multiprocessing

import ansible


ANSIBLE_VERSION = tuple(map(int, ansible.__version__.split('.')))

if ANSIBLE_VERSION >= (2, 0):
    from ansible.plugins.callback import CallbackBase
else:
    CallbackBase = object


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'goodplay'

    def __init__(self, *args, **kwargs):
        super(CallbackModule, self).__init__(*args, **kwargs)

        self.previous_task = None
        self.previously_ended_task = None
        self.task = None

        # need to use shared dict here as ansible v1 runner callbacks
        # are called from different processes (depending on number of forks)
        self.test_task_outcomes = multiprocessing.Manager().dict()

    def display(self, msg):
        if ANSIBLE_VERSION >= (2, 0):
            self._display.display(msg)
        else:
            from ansible.callbacks import display
            display(msg)

    # handle test task outcome

    def reset_test_task_outcome(self):
        self.test_task_outcomes.clear()

    def add_test_task_host_outcome(self, host, outcome, res=None):
        self.test_task_outcomes[host] = dict(outcome=outcome, res=res)

    def final_test_task_outcome(self):
        if self.test_task_outcomes:
            outcomes = \
                set((x['outcome'] for x in self.test_task_outcomes.values()))
            prioritized_outcome_order = ('failed', 'skipped', 'passed')
            for outcome in prioritized_outcome_order:
                if outcome in outcomes:
                    return outcome

        return 'skipped'

    # ansible playbook-specific callback methods

    def v2_playbook_on_task_start(self, task, is_conditional):
        # ensure task is available as attribute on instance as in ansible v1
        self.task = task

        self.playbook_on_task_start(task.name, is_conditional)

    def playbook_on_task_start(self, name, is_conditional):
        self.check_and_handle_playbook_on_task_end()

        if self.is_test_task(self.task):
            self.playbook_on_test_task_start(self.task)

    def check_and_handle_playbook_on_task_end(self):
        if self.previous_task and \
                self.previously_ended_task != self.previous_task:
            self.playbook_on_task_end(self.previous_task)
            self.previously_ended_task = self.previous_task

        self.previous_task = self.task

    def is_test_task(self, task):
        # task can be None for meta tasks (e.g. setup)
        return task and getattr(task, 'name') and 'test' in task.tags

    def playbook_on_test_task_start(self, task):
        self.send_event('test-task-start', name=task.name)

    def send_event(self, event_name, **kwargs):
        event_line_prefix = 'GOODPLAY => '
        event_json = json.dumps(dict(event_name=event_name, data=kwargs))
        msg = event_line_prefix + event_json
        self.display(msg)

    def playbook_on_task_end(self, task):
        if self.is_test_task(task):
            self.playbook_on_test_task_end(task)

    def playbook_on_test_task_end(self, task):
        outcome = self.final_test_task_outcome()

        self.send_event('test-task-end', name=task.name, outcome=outcome)
        self.reset_test_task_outcome()

    def playbook_on_play_start(self, name):
        self.check_and_handle_playbook_on_task_end()

    def playbook_on_stats(self, stats):
        self.check_and_handle_playbook_on_task_end()

    # ansible runner-specific callback methods

    def runner_on_failed(self, host, res, ignore_errors=False):
        if ignore_errors:
            return

        if self.is_test_task(self.task):
            self.add_test_task_host_outcome(host, 'failed', res)
        else:
            self.send_event('error', message=str(res))

    def runner_on_ok(self, host, res):
        if self.is_test_task(self.task):
            if res.get('changed') or res.get('rc', 0) != 0:
                self.add_test_task_host_outcome(host, 'failed', res)
            else:
                self.add_test_task_host_outcome(host, 'passed', res)

    def runner_on_skipped(self, host, item=None):
        if self.is_test_task(self.task):
            self.add_test_task_host_outcome(host, 'skipped')

    def runner_on_unreachable(self, host, res):
        if self.is_test_task(self.task):
            self.add_test_task_host_outcome(host, 'failed', res)
        else:
            self.send_event('error', message=str(res))
