# -*- coding: utf-8 -*-

import docker
import docker.errors
import docker.utils

import pytest


pytest_plugins = 'pytester'


@pytest.fixture
def docker_client(mocker):
    proxy_method_names = (
        'inspect_image',
        'pull',
        'remove_container',
        'start',
    )

    client = docker.Client(
        **docker.utils.kwargs_from_env(assert_hostname=False))

    for proxy_method_name in proxy_method_names:
        origin_method = getattr(client, proxy_method_name)
        mocker.patch.object(client, proxy_method_name).side_effect = \
            origin_method

    mocker.patch('docker.Client').return_value = client

    return client


@pytest.fixture
def docker_client_unavailable(mocker):
    client = docker.Client(base_url='unix://tmp/docker.unavailable.sock')

    mocker.patch('docker.Client').return_value = client

    return client


def create_playbook_and_run(testdir, playbook, inventory=None):
    if inventory:
        testdir.makefile('', inventory=inventory)
    testdir.makefile('.yml', test_playbook=playbook)

    return testdir.inline_run('-s')


def test_docker_is_not_initialized_when_not_used(testdir, mocker):
    mock_docker_client = mocker.patch('docker.Client', autospec=True)

    result = create_playbook_and_run(testdir, '''---
- hosts: default
  tasks:
    - name: host is reachable
      ping:
      tags: test
''', inventory='default ansible_connection=local')

    result.assertoutcome(passed=1)

    assert not mock_docker_client.called


def test_docker_is_not_initialized_when_collect_only(testdir, mocker):
    mock_docker_client = mocker.patch('docker.Client', autospec=True)

    testdir.makefile(
        '', inventory='guesthostname goodplay_image=busybox:latest')
    testdir.makefile('.yml', test_playbook='''---
- hosts: guesthostname
  gather_facts: no

  tasks:
    - name: task 1
      raw: "ls -la /"
      changed_when: False
      tags: test
''')

    items, result = testdir.inline_genitems()

    result.assertoutcome()
    assert len(items) == 1
    assert items[0].name == 'task 1'

    assert not mock_docker_client.called


def test_docker_used_and_not_available(
        testdir, docker_client_unavailable):
    result = create_playbook_and_run(testdir, '''---
- hosts: guesthostname
  gather_facts: no

  tasks:
    - name: task 1
      raw: "ls -la /"
      changed_when: False
      tags: test
''', inventory='guesthostname goodplay_image=busybox:latest')

    result.assertoutcome(failed=1)


def test_docker_pull_called_when_image_does_not_exist(
        testdir, docker_client):
    docker_client.inspect_image.side_effect = \
        docker.errors.NotFound('image not found', None,
                               explanation='simulate missing docker image')

    result = create_playbook_and_run(testdir, '''---
- hosts: guesthostname
  gather_facts: no

  tasks:
    - name: task 1
      raw: "ls -la /"
      changed_when: False
      tags: test
''', inventory='guesthostname goodplay_image=busybox:latest')

    result.assertoutcome(passed=1)

    docker_client.inspect_image.assert_called_once_with('busybox:latest')
    docker_client.pull.assert_called_once_with('busybox:latest')


def test_docker_pull_is_called_once_per_image_when_multiple_times(
        testdir, docker_client):
    docker_client.inspect_image.side_effect = \
        docker.errors.NotFound('image not found', None,
                               explanation='simulate missing docker image')

    result = create_playbook_and_run(testdir, '''---
- hosts: guesthostname1:guesthostname2
  gather_facts: no

  tasks:
    - name: task 1
      raw: "ls -la /"
      changed_when: False
      tags: test
''', inventory='''guesthostname1 goodplay_image=busybox:latest
guesthostname2 goodplay_image=busybox:latest
''')

    result.assertoutcome(passed=1)

    docker_client.inspect_image.assert_called_once_with('busybox:latest')
    docker_client.pull.assert_called_once_with('busybox:latest')


def test_docker_pull_not_called_when_image_already_exists(
        testdir, docker_client):
    # ensure image is present
    docker_client.pull('busybox:latest')
    docker_client.pull.reset_mock()

    result = create_playbook_and_run(testdir, '''---
- hosts: guesthostname
  gather_facts: no

  tasks:
    - name: task 1
      raw: "ls -la /"
      changed_when: False
      tags: test
''', inventory='guesthostname goodplay_image=busybox:latest')

    result.assertoutcome(passed=1)

    docker_client.inspect_image.assert_called_once_with('busybox:latest')
    docker_client.pull.assert_not_called()


def test_started_docker_container_is_removed_after_successful_run(
        testdir, docker_client):
    result = create_playbook_and_run(testdir, '''---
- hosts: guesthostname
  gather_facts: no

  tasks:
    - name: task 1
      raw: "ls -la /"
      changed_when: False
      tags: test
''', inventory='guesthostname goodplay_image=busybox:latest')

    result.assertoutcome(passed=1)

    assert docker_client.start.call_count == 1

    started_container_id = docker_client.start.call_args[0][0]
    docker_client.remove_container.assert_called_once_with(
        started_container_id, force=True)


def test_started_docker_container_is_removed_after_failed_run(
        testdir, docker_client):
    result = create_playbook_and_run(testdir, '''---
- hosts: guesthostname
  gather_facts: no

  tasks:
    - name: intentionally failing task
      raw: who
      failed_when: True
      tags: test
''', inventory='guesthostname goodplay_image=busybox:latest')

    result.assertoutcome(failed=1)

    assert docker_client.start.call_count == 1

    started_container_id = docker_client.start.call_args[0][0]
    docker_client.remove_container.assert_called_once_with(
        started_container_id, force=True)


def test_group_vars_directory_beside_inventory_file_is_incorporated(testdir):
    group_vars_path = testdir.tmpdir.mkdir('group_vars')
    group_vars_path.join('all').write('hello: world')

    result = create_playbook_and_run(testdir, '''---
- hosts: guesthostname
  gather_facts: no

  tasks:
    - name: task 1
      raw: 'echo -n {{ hello }}'
      register: echo_result
      failed_when: echo_result.stdout != 'world'
      changed_when: False
      tags: test
''', inventory='guesthostname goodplay_image=busybox:latest')

    result.assertoutcome(passed=1)


def test_group_vars_directory_beside_inventory_directory_is_incorporated(
        testdir):
    inventory_path = testdir.tmpdir.mkdir('inventory')
    inventory_path.join('static').write(
        'guesthostname goodplay_image=busybox:latest')

    group_vars_path = inventory_path.mkdir('group_vars')
    group_vars_path.join('all').write('hello: world')

    result = create_playbook_and_run(testdir, '''---
- hosts: guesthostname
  gather_facts: no

  tasks:
    - name: task 1
      raw: 'echo -n {{ hello }}'
      register: echo_result
      failed_when: echo_result.stdout != 'world'
      changed_when: False
      tags: test
''')

    result.assertoutcome(passed=1)


def test_host_vars_directory_beside_inventory_file_is_incorporated(testdir):
    host_vars_path = testdir.tmpdir.mkdir('host_vars')
    host_vars_path.join('guesthostname').write('hello: world')

    result = create_playbook_and_run(testdir, '''---
- hosts: guesthostname
  gather_facts: no

  tasks:
    - name: task 1
      raw: 'echo -n {{ hello }}'
      register: echo_result
      failed_when: echo_result.stdout != 'world'
      changed_when: False
      tags: test
''', inventory='guesthostname goodplay_image=busybox:latest')

    result.assertoutcome(passed=1)


def test_host_vars_directory_beside_inventory_directory_is_incorporated(
        testdir):
    inventory_path = testdir.tmpdir.mkdir('inventory')
    inventory_path.join('static').write(
        'guesthostname goodplay_image=busybox:latest')

    host_vars_path = inventory_path.mkdir('host_vars')
    host_vars_path.join('guesthostname').write('hello: world')

    result = create_playbook_and_run(testdir, '''---
- hosts: guesthostname
  gather_facts: no

  tasks:
    - name: task 1
      raw: 'echo -n {{ hello }}'
      register: echo_result
      failed_when: echo_result.stdout != 'world'
      changed_when: False
      tags: test
''')

    result.assertoutcome(passed=1)


# def test_extended_inventory_path_is_removed_after_test(testdir):
#     pass
