# -*- coding: utf-8 -*-

import pytest

pytestmark = pytest.mark.integration
pytest_plugins = 'pytester'


def test_junitxml_removes_classname_yml_extension(testdir):
    testdir.makefile('', inventory='127.0.0.1 ansible_connection=local')
    testdir.makefile('.yml', test_playbook='''---
- hosts: 127.0.0.1
  tasks:
    - name: host is reachable
      ping:
      tags: test
''')

    junit_xml_path = testdir.tmpdir.join('junit.xml')

    testdir.inline_run('--junitxml=' + str(junit_xml_path))

    junit_xml_content = junit_xml_path.read()
    assert 'classname="test_playbook"' in junit_xml_content


def test_junitxml_does_not_remove_task_name_with_yml_extension(testdir):
    testdir.makefile('', inventory='127.0.0.1 ansible_connection=local')
    testdir.makefile('.yml', test_playbook='''---
- hosts: 127.0.0.1
  tasks:
    - name: update appconfig.yml
      ping:
      tags: test
''')

    junit_xml_path = testdir.tmpdir.join('junit.xml')

    testdir.inline_run('--junitxml=' + str(junit_xml_path))

    junit_xml_content = junit_xml_path.read()
    assert 'name="update appconfig.yml"' in junit_xml_content
