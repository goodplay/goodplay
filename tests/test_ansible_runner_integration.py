# -*- coding: utf-8 -*-

import logging

import pytest

from goodplay_helpers import smart_create

pytestmark = pytest.mark.integration


def test_goodplay_info_is_logged_to_stdout_and_logging(testdir, caplog, capfd):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          ping:
          tags: test
    ''')

    testdir.inline_run('-s')

    message = 'soft dependencies file not found at {0!s} ... nothing to install'.format(
        testdir.tmpdir.join('requirements.yml'))

    # capfd needs to be used here as logging module seems to use fd
    stdout, _ = capfd.readouterr()
    # assert message is exactly once in stdout (no double logging occurs)
    assert stdout.count(message) == 1

    assert ('goodplay.ansible_support.playbook', logging.INFO, message) in caplog.record_tuples


def test_goodplay_info_is_logged_to_stdout_when_logging_is_not_configured(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          ping:
          tags: test
    ''')

    result = testdir.runpytest_subprocess('-s')

    assert len([line for line in result.stdout.lines
                if 'soft dependencies file not found at ' in line]) == 1


def test_passed_on_non_changed_task(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


def test_passed_multiple_on_previously_changed_task(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          ping:
          changed_when: True
          tags: test

        - name: task2
          ping:
          tags: test

        - name: task3
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=2, failed=1)


def test_passed_on_previously_changed_non_test_task(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: intentionally changed task
          ping:
          changed_when: True

        - name: task1
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


def test_passed_on_previously_skipped_non_test_task(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: intentionally skipped task
          ping:
          when: False

        - name: task1
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


def test_passed_on_previously_failed_non_test_task_with_ignore_errors(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: intentionally failed task
          ping:
          failed_when: True
          ignore_errors: yes

        - name: task1
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


def test_passed_on_multiple_plays(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          ping:
          tags: test

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task2
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=2)


def test_passed_with_gather_facts_enabled(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: yes
      tasks:
        - name: task1
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


def test_passed_with_gather_facts_disabled(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


def test_skipped_outcome_takes_priority_over_passed(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    host1 ansible_connection=local
    host2 ansible_connection=local

    ## test_playbook.yml
    - hosts: host1
      gather_facts: no
      tasks:
        - name: avoid all test tasks skipped
          ping:
          tags: test

    - hosts: host1:host2
      gather_facts: no
      tasks:
        - name: task2
          ping:
          when: inventory_hostname != 'host2'
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1, skipped=1)


def test_skipped_on_previously_failed_non_test_task(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: intentionally failed task
          ping:
          failed_when: True

        - name: task1
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(skipped=1, failed=1)


def test_skipped_multiple_on_previously_failed_non_test_task(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: intentionally failed task
          ping:
          failed_when: True

        - name: task1
          ping:
          tags: test

        - name: task2
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(skipped=2, failed=1)


def test_failed_on_changed_task(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          ping:
          changed_when: True
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)


def test_failed_on_failed_task(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          ping:
          failed_when: True
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)


def test_passed_on_wait_for_success(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: create .pid file
          file:
            path: "{{ playbook_dir }}/.pid"
            state: touch

        - name: task1
          wait_for:
            path: "{{ playbook_dir }}/.pid"
            timeout: 5
          tags: test

        - name: task2
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=2)


def test_passed_on_include_playbook(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## playbook_to_include.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: create .pid file
          file:
            path: "{{ playbook_dir }}/.pid"
            state: touch

    ## test_playbook.yml
    - include: playbook_to_include.yml

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          wait_for:
            path: "{{ playbook_dir }}/.pid"
            timeout: 5
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


def test_passed_on_import_playbook(testdir):
    pytest.importorskip('ansible.release', minversion='2.4')

    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## playbook_to_import.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: create .pid file
          file:
            path: "{{ playbook_dir }}/.pid"
            state: touch

    ## test_playbook.yml
    - import_playbook: playbook_to_import.yml

    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          wait_for:
            path: "{{ playbook_dir }}/.pid"
            timeout: 5
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


def test_failed_on_wait_for_timeout(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          wait_for:
            path: /path/to/some/nonexisting/file
            timeout: 0
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)


def test_wait_for_task_timeout_does_not_stop_test_run(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          wait_for:
            port: 143
            timeout: 1
          tags: test

        - name: task2
          ping:
          tags: test

        - name: task3
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=2, failed=1)


def test_wait_for_task_timeout_does_not_stop_test_run_with_multiple_hosts(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    localhost1 ansible_connection=local
    localhost2 ansible_connection=local

    ## test_playbook.yml
    - hosts: localhost1:localhost2
      gather_facts: no
      tasks:
        - name: task1
          wait_for:
            port: 143
            timeout: 1
          tags: test

        - name: task2
          ping:
          tags: test

        - name: task3
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=2, failed=1)


def test_failed_on_unreachable_host_on_gather_facts(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    unreachable.host.local

    ## test_playbook.yml
    - hosts: unreachable.host.local
      gather_facts: yes
      tasks:
        - name: task1
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(skipped=1, failed=1)


def test_failed_on_single_failed_host(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    host1 ansible_connection=local
    host2 ansible_connection=local

    ## test_playbook.yml
    - hosts: host1:host2
      gather_facts: no
      tasks:
        - name: task1
          ping:
          failed_when: inventory_hostname == 'host1'
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)


def test_failed_on_all_tasks_skipped(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: unknownhost
      gather_facts: no
      tasks:
        - name: task1
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(skipped=1, failed=1)
    assert 'Failed: all test tasks have been skipped' in \
        str(result.getfailures()[0].longrepr)


def test_failed_outcome_takes_highest_priority(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    host1 ansible_connection=local
    host2 ansible_connection=local
    host3 ansible_connection=local

    ## test_playbook.yml
    - hosts: host1:host2:host3
      gather_facts: no
      tasks:
        - name: task1
          ping:
          when: inventory_hostname != 'host2'
          failed_when: inventory_hostname == 'host3'
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)


def test_failed_on_failing_non_test_task_after_passed_test_task(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          ping:
          tags: test

        - name: intentionally failed task
          ping:
          failed_when: True
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1, failed=1)


def test_ansible_stdout_is_fully_consumed(testdir, capsys):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          ping:
          tags: test

        - name: intentionally failed task
          ping:
          failed_when: True
    ''')

    testdir.inline_run('-s')
    stdout, _ = capsys.readouterr()
    ansible_play_recap_part = 'failed=1'
    assert ansible_play_recap_part in stdout


def test_ansible_retry_files_are_disabled(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          ping:
          failed_when: True
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)

    assert not testdir.tmpdir.join('test_playbook.retry').check()


def test_goodplay_traceback_is_absent(testdir, capsys):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: task1
          ping:
          tags: test

        - name: intentionally failed task
          ping:
          failed_when: True

    ## test_something.py
    def please_fail():
        raise Exception()

    def test_something():
        please_fail()
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1, failed=2)

    stdout, _ = capsys.readouterr()
    stacktrace_entry_separator_count = \
        len([line for line in stdout.splitlines() if line.startswith('_ _ _ _ ')])

    # assert only single stacktrace entry separator for failing Python test
    assert stacktrace_entry_separator_count == 1
