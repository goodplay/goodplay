# -*- coding: utf-8 -*-

import subprocess

from goodplay_helpers import smart_create


def test_goodplay_runs_fine_without_any_warnings(tmpdir):
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
        ['goodplay'], cwd=str(tmpdir))

    assert b'warning' not in stdout
