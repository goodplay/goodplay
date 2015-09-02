# -*- coding: utf-8 -*-

pytest_plugins = 'pytester'


def create_playbook_and_run(testdir, playbook, inventory=None):
    if not inventory:
        inventory = '127.0.0.1 ansible_connection=local'
    testdir.makefile('', inventory=inventory)
    testdir.makefile('.yml', test_playbook=playbook)

    return testdir.inline_run('-s')


def test_passed_on_non_changed_task(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: 127.0.0.1
  tasks:
    - name: task1
      ping:
      tags: test
''')

    assert result.countoutcomes() == [1, 0, 0]


def test_passed_on_previously_changed_non_test_task(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: 127.0.0.1
  tasks:
    - name: intentionally changed task
      ping:
      changed_when: True

    - name: task1
      ping:
      tags: test
''')

    assert result.countoutcomes() == [1, 0, 0]


def test_passed_on_previously_skipped_non_test_task(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: 127.0.0.1
  tasks:
    - name: intentionally skipped task
      ping:
      when: False

    - name: task1
      ping:
      tags: test
''')

    assert result.countoutcomes() == [1, 0, 0]


def test_passed_on_previously_failed_non_test_task_with_ignore_errors(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: 127.0.0.1
  tasks:
    - name: intentionally failed task
      ping:
      failed_when: True
      ignore_errors: yes

    - name: task1
      ping:
      tags: test
''')

    assert result.countoutcomes() == [1, 0, 0]


def test_passed_on_multiple_plays(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: 127.0.0.1
  tasks:
    - name: task1
      ping:
      tags: test

- hosts: 127.0.0.1
  tasks:
    - name: task2
      ping:
      tags: test
''')

    assert result.countoutcomes() == [2, 0, 0]


def test_passed_without_gather_facts(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: 127.0.0.1
  gather_facts: no
  tasks:
    - name: task1
      ping:
      tags: test
''')

    assert result.countoutcomes() == [1, 0, 0]


def test_skipped_outcome_takes_priority_over_passed(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: host1
  tasks:
    - name: avoid all test tasks skipped
      ping:
      tags: test

- hosts: host1:host2
  tasks:
    - name: task2
      ping:
      when: inventory_hostname != 'host2'
      tags: test
''', inventory='''host1 ansible_connection=local
host2 ansible_connection=local
''')

    assert result.countoutcomes() == [1, 1, 0]


def test_skipped_on_previously_failed_non_test_task(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: 127.0.0.1
  tasks:
    - name: intentionally failed task
      ping:
      failed_when: True

    - name: task1
      ping:
      tags: test
''')

    assert result.countoutcomes() == [0, 1, 1]


def test_skipped_multiple_on_previously_failed_non_test_task(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: 127.0.0.1
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

    assert result.countoutcomes() == [0, 2, 1]


def test_failed_on_changed_task(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: 127.0.0.1
  tasks:
    - name: task1
      ping:
      changed_when: True
      tags: test
''')

    assert result.countoutcomes() == [0, 0, 1]


def test_failed_on_failed_task(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: 127.0.0.1
  tasks:
    - name: task1
      ping:
      failed_when: True
      tags: test
''')

    assert result.countoutcomes() == [0, 0, 1]


def test_failed_on_wait_for_timeout(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: 127.0.0.1
  tasks:
    - name: task1
      wait_for:
        path: /path/to/some/nonexisting/file
        timeout: 0
      tags: test
''')

    assert result.countoutcomes() == [0, 0, 1]


def test_failed_on_unreachable_host_on_gather_facts(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: unreachable.host.local
  tasks:
    - name: task1
      ping:
      tags: test
''', inventory='unreachable.host.local')

    assert result.countoutcomes() == [0, 1, 1]


def test_failed_on_single_failed_host(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: host1:host2
  tasks:
    - name: task1
      ping:
      failed_when: inventory_hostname == 'host1'
      tags: test
''', inventory='''host1 ansible_connection=local
host2 ansible_connection=local
''')

    assert result.countoutcomes() == [0, 0, 1]


def test_failed_on_all_tasks_skipped(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: unknownhost
  tasks:
    - name: task1
      ping:
      tags: test
''')

    assert result.countoutcomes() == [0, 1, 1]
    assert 'Failed: all test tasks have been skipped' in \
        str(result.getfailures()[0].longrepr)


def test_failed_outcome_takes_highest_priority(testdir):
    result = create_playbook_and_run(testdir, '''---
- hosts: host1:host2:host3
  tasks:
    - name: task1
      ping:
      when: inventory_hostname != 'host2'
      failed_when: inventory_hostname == 'host3'
      tags: test
''', inventory='''host1 ansible_connection=local
host2 ansible_connection=local
host3 ansible_connection=local
''')

    assert result.countoutcomes() == [0, 0, 1]
