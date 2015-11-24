# -*- coding: utf-8 -*-

import json

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'goodplay'

    def __init__(self, *args, **kwargs):
        super(CallbackModule, self).__init__(*args, **kwargs)

        self.previous_task = None
        self.previously_ended_task = None
        self.task = None

        self.reset_per_host_outcomes()

    # ansible playbook-specific callback methods

    def v2_playbook_on_task_start(self, task, is_conditional):
        # ensure task is available as attribute on instance
        self.task = task

        self.check_and_handle_playbook_on_task_end()

        if self.is_test_task(self.task):
            self.playbook_on_test_task_start(self.task)

    def check_and_handle_playbook_on_task_end(self):
        if self.previous_task and self.previously_ended_task != self.previous_task:
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
        self._display.display(msg)

    def playbook_on_task_end(self, task):
        if self.is_test_task(task):
            self.playbook_on_test_task_end(task)

    def playbook_on_test_task_end(self, task):
        outcome = self.final_test_task_outcome()

        self.send_event('test-task-end', name=task.name, outcome=outcome)
        self.reset_per_host_outcomes()

    def v2_playbook_on_play_start(self, play):
        self.check_and_handle_playbook_on_task_end()

    def v2_playbook_on_stats(self, stats):
        self.check_and_handle_playbook_on_task_end()

    # ansible runner-specific callback methods

    def runner_on_failed(self, host, res, ignore_errors=False):
        if ignore_errors:
            return

        self.handle_failed_result(host, res)

    def runner_on_ok(self, host, res):
        changed = res.get('changed')

        if changed:
            self.handle_changed_result(host, res)
        else:
            self.handle_non_changed_result(host, res)

    def runner_on_skipped(self, host, item=None):
        self.handle_skipped_result(host)

    def runner_on_unreachable(self, host, res):
        self.handle_failed_result(host, res)

    # handle results and outcome

    def reset_per_host_outcomes(self):
        self.per_host_outcomes = {}

    def add_per_host_outcome(self, host, outcome, res=None):
        self.per_host_outcomes[host] = dict(outcome=outcome, res=res)

    def final_test_task_outcome(self):
        if self.per_host_outcomes:
            outcomes = set(x['outcome'] for x in self.per_host_outcomes.values())
            outcome_priority = ('failed', 'skipped', 'passed')
            for outcome in outcome_priority:
                if outcome in outcomes:
                    return outcome

        return 'skipped'

    def handle_changed_result(self, host, res):
        self.check_and_handle_test_task(host, 'failed', res)

    def handle_non_changed_result(self, host, res):
        self.check_and_handle_test_task(host, 'passed', res)

    def handle_skipped_result(self, host):
        self.check_and_handle_test_task(host, 'skipped')

    def handle_failed_result(self, host, res):
        if not self.check_and_handle_test_task(host, 'failed', res):
            self.send_event('error', message=str(res))

    def check_and_handle_test_task(self, host, outcome, res=None):
        if self.is_test_task(self.task):
            self.add_per_host_outcome(host, outcome, res)
            return True
        return False
