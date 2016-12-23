# -*- coding: utf-8 -*-

import subprocess

from goodplay_helpers import smart_create


def test_goodplay_cli_args_are_forwarded_to_pytest(tmpdir):
    smart_create(tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - name: task1
          ping:
          tags: test
    ''')

    stdout = subprocess.check_output(
        ['goodplay', '--collect-only'], cwd=str(tmpdir))
    expected = b"<GoodplayTest 'task1'>"

    assert expected in stdout


def test_goodplay_cli_does_not_collect_python_tests(tmpdir):
    smart_create(tmpdir, '''
    ## test_somepython.py
    def test_something_python_related():
        pass
    ''')

    # pytest's exit code when no tests have been collected
    EXIT_NOTESTSCOLLECTED = 5

    goodplay_returncode = subprocess.call(
        ['goodplay'], cwd=str(tmpdir))

    assert goodplay_returncode == EXIT_NOTESTSCOLLECTED


def test_goodplay_cli_recursively_collects_from_subdirectories(tmpdir):
    smart_create(tmpdir, '''
    ## some/subdir/inventory
    127.0.0.1 ansible_connection=local

    ## some/subdir/test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - name: task1
          ping:
          tags: test
    ''')

    stdout = subprocess.check_output(
        ['goodplay', '--collect-only'], cwd=str(tmpdir))
    expected = b"<GoodplayTest 'task1'>"

    assert expected in stdout


def test_goodplay_cli_forwards_pytest_returncode(tmpdir):
    # pytest's exit code when no tests have been collected
    EXIT_NOTESTSCOLLECTED = 5

    goodplay_returncode = subprocess.call(
        ['goodplay'], cwd=str(tmpdir))

    assert goodplay_returncode == EXIT_NOTESTSCOLLECTED
