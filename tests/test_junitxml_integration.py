# -*- coding: utf-8 -*-

import pytest

from goodplay_helpers import smart_create

pytestmark = pytest.mark.integration


def test_junitxml_removes_classname_yml_extension(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: host is reachable
          ping:
          tags: test
    ''')

    junit_xml_path = testdir.tmpdir.join('junit.xml')

    testdir.inline_run('--junitxml', str(junit_xml_path))
    junit_xml_content = junit_xml_path.read()
    assert 'classname="test_playbook"' in junit_xml_content


def test_junitxml_does_not_remove_task_name_with_yml_extension(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: update appconfig.yml
          ping:
          tags: test
    ''')

    junit_xml_path = testdir.tmpdir.join('junit.xml')

    testdir.inline_run('--junitxml', str(junit_xml_path))
    junit_xml_content = junit_xml_path.read()
    assert 'name="update appconfig.yml"' in junit_xml_content
