# -*- coding: utf-8 -*-

import pytest

from goodplay_helpers import smart_create

pytestmark = pytest.mark.integration


def test_nodeid_no_platform(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: all
      tasks:
        - name: task1
          ping:
          tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 1
    assert items[0].nodeid == 'test_playbook.yml::task1'


def test_nodeid_with_platform(testdir):
    smart_create(testdir.tmpdir, '''
    ## role1/meta/main.yml
    galaxy_info:
      author: John Doe
      platforms:
        - name: EL
          versions:
            - 6
            - 7
    dependencies: []

    ## role1/tasks/main.yml
    - ping:

    ## role1/tests/.goodplay.yml
    platforms:
      - name: EL
        version: 6
        image: centos:centos6

      - name: EL
        version: 7
        image: centos:centos7

    ## role1/tests/inventory
    default goodplay_platform=*

    ## role1/tests/test_playbook.yml
    ---
    - hosts: default
      tasks:
        - name: host is reachable
          ping:
          tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 2
    assert items[0].nodeid == 'role1/tests/test_playbook.yml::EL:6::host is reachable'
    assert items[1].nodeid == 'role1/tests/test_playbook.yml::EL:7::host is reachable'
