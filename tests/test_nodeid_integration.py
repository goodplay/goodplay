# -*- coding: utf-8 -*-

import pytest
import yaml

pytestmark = pytest.mark.integration
pytest_plugins = 'pytester'


@pytest.mark.integration
def test_nodeid_no_platform(testdir):
    testdir.makefile('', inventory='all')
    testdir.makefile('.yml', test_playbook='''---
- hosts: all
  tasks:
    - name: task1
      ping:
      tags: test
''')

    items, result = testdir.inline_genitems()

    assert len(items) == 1
    assert items[0].nodeid == 'test_playbook.yml::task1'

    result.assertoutcome()


@pytest.mark.integration
def test_nodeid_with_platform(testdir):
    role_path = testdir.tmpdir

    # create role meta
    meta_info = {
        'galaxy_info': {
            'author': 'John Doe',
            'platforms': [{
                'name': 'EL',
                'versions': [6, 7]
            }]
        },
        'dependencies': [],
    }
    role_path.join('meta', 'main.yml').write(yaml.dump(meta_info), ensure=True)

    # create role tasks
    role_path.join('tasks', 'main.yml').write('''---
- ping:
''', ensure=True)

    # create goodplay config
    role_path.join('tests', '.goodplay.yml').write('''---
platforms:
  - name: EL
    version: 6
    image: centos:centos6

  - name: EL
    version: 7
    image: centos:centos7
''', ensure=True)

    # create role tests
    role_path.join('tests', 'inventory').write(
        'default goodplay_platform=*', ensure=True)
    role_path.join('tests', 'test_playbook.yml').write('''---
- hosts: default
  tasks:
    - name: host is reachable
      ping:
      tags: test
''', ensure=True)

    items, result = testdir.inline_genitems()

    assert len(items) == 2
    assert items[0].nodeid == 'tests/test_playbook.yml::EL:6::host is reachable'
    assert items[1].nodeid == 'tests/test_playbook.yml::EL:7::host is reachable'

    result.assertoutcome()
