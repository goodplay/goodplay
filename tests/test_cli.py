# -*- coding: utf-8 -*-

import subprocess


def test_goodplay_cli_args_are_forwarded_to_pytest(tmpdir):
    tmpdir.join('inventory').write(
        '127.0.0.1 ansible_connection=local', ensure=True)

    tmpdir.join('test_playbook.yml').write('''---
- hosts: 127.0.0.1
  tasks:
    - name: task1
      ping:
      tags: test
''', ensure=True)

    stdout = subprocess.check_output(
        ['goodplay', '--collect-only'], cwd=str(tmpdir))
    expected = "<GoodplayTest 'task1'>"

    assert expected in stdout


def test_goodplay_cli_does_not_collect_python_tests(tmpdir):
    tmpdir.join('test_somepython.py').write('''
def test_something_python_related():
    pass
''', ensure=True)

    # pytest's exit code when no tests have been collected
    EXIT_NOTESTSCOLLECTED = 5

    goodplay_returncode = subprocess.call(
        ['goodplay'], cwd=str(tmpdir))

    assert goodplay_returncode == EXIT_NOTESTSCOLLECTED


def test_goodplay_cli_recursively_collects_from_subdirectories(tmpdir):
    tmpdir.join('some', 'subdir', 'inventory').write(
        '127.0.0.1 ansible_connection=local', ensure=True)

    tmpdir.join('some', 'subdir', 'test_playbook.yml').write('''---
- hosts: 127.0.0.1
  tasks:
    - name: task1
      ping:
      tags: test
''', ensure=True)

    stdout = subprocess.check_output(
        ['goodplay', '--collect-only'], cwd=str(tmpdir))
    expected = "<GoodplayTest 'task1'>"

    assert expected in stdout


def test_goodplay_cli_forwards_pytest_returncode(tmpdir):
    # pytest's exit code when no tests have been collected
    EXIT_NOTESTSCOLLECTED = 5

    goodplay_returncode = subprocess.call(
        ['goodplay'], cwd=str(tmpdir))

    assert goodplay_returncode == EXIT_NOTESTSCOLLECTED
