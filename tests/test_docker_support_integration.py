# -*- coding: utf-8 -*-

import docker
import docker.errors
import docker.utils
import pytest

from goodplay_helpers import smart_create

pytestmark = pytest.mark.integration


@pytest.fixture
def docker_client(mocker):
    proxy_method_names = (
        'create_container',
        'inspect_image',
        'pull',
        'remove_container',
        'start',
    )

    client = docker.Client(
        version='auto',
        **docker.utils.kwargs_from_env(assert_hostname=False))

    for proxy_method_name in proxy_method_names:
        origin_method = getattr(client, proxy_method_name)
        mocker.patch.object(client, proxy_method_name).side_effect = origin_method

    mocker.patch('docker.Client').return_value = client

    return client


@pytest.fixture
def docker_client_unavailable(mocker):
    client = docker.Client(base_url='unix://tmp/docker.unavailable.sock')

    mocker.patch('docker.Client').return_value = client

    return client


def test_docker_is_not_initialized_when_not_used(testdir, mocker):
    mock_docker_client = mocker.patch('docker.Client', autospec=True)

    smart_create(testdir.tmpdir, '''
    ## inventory
    default ansible_connection=local

    ## test_playbook.yml
    - hosts: default
      gather_facts: no
      tasks:
        - name: host is reachable
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)

    assert not mock_docker_client.called


def test_docker_is_not_initialized_when_collect_only(testdir, mocker):
    mock_docker_client = mocker.patch('docker.Client', autospec=True)

    smart_create(testdir.tmpdir, '''
    ## inventory
    guesthostname goodplay_image=busybox:latest

    ## test_playbook.yml
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


def test_docker_used_and_not_available(testdir, docker_client_unavailable):
    smart_create(testdir.tmpdir, '''
    ## inventory
    guesthostname goodplay_image=busybox:latest

    ## test_playbook.yml
    - hosts: guesthostname
      gather_facts: no
      tasks:
        - name: task 1
          raw: "ls -la /"
          changed_when: False
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)


def test_docker_pull_called_when_image_does_not_exist(testdir, docker_client):
    docker_client.inspect_image.side_effect = \
        docker.errors.NotFound('image not found', None,
                               explanation='simulate missing docker image')

    smart_create(testdir.tmpdir, '''
    ## inventory
    guesthostname goodplay_image=busybox:latest ansible_user=root

    ## test_playbook.yml
    - hosts: guesthostname
      gather_facts: no
      tasks:
        - name: task 1
          raw: "ls -la /"
          changed_when: False
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)

    docker_client.inspect_image.assert_called_once_with('busybox:latest')
    docker_client.pull.assert_called_once_with('busybox:latest')


def test_docker_pull_is_called_once_per_image_when_multiple_times(testdir, docker_client):
    docker_client.inspect_image.side_effect = \
        docker.errors.NotFound('image not found', None,
                               explanation='simulate missing docker image')

    smart_create(testdir.tmpdir, '''
    ## inventory
    guesthostname1 goodplay_image=busybox:latest ansible_user=root
    guesthostname2 goodplay_image=busybox:latest ansible_user=root

    ## test_playbook.yml
    - hosts: guesthostname1:guesthostname2
      gather_facts: no
      tasks:
        - name: task 1
          raw: "ls -la /"
          changed_when: False
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)

    docker_client.inspect_image.assert_called_once_with('busybox:latest')
    docker_client.pull.assert_called_once_with('busybox:latest')


def test_docker_pull_not_called_when_image_already_exists(testdir, docker_client):
    # ensure image is present
    docker_client.pull('busybox:latest')
    docker_client.pull.reset_mock()

    smart_create(testdir.tmpdir, '''
    ## inventory
    guesthostname goodplay_image=busybox:latest ansible_user=root

    ## test_playbook.yml
    - hosts: guesthostname
      gather_facts: no
      tasks:
        - name: task 1
          raw: "ls -la /"
          changed_when: False
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)

    docker_client.inspect_image.assert_called_once_with('busybox:latest')
    docker_client.pull.assert_not_called()


def test_failed_when_goodplay_platform_cannot_be_resolved(testdir, docker_client):
    smart_create(testdir.tmpdir, '''
    ## inventory
    guesthostname goodplay_platform=thename:theversion

    ## test_playbook.yml
    - hosts: guesthostname
      gather_facts: no
      tasks:
        - name: task 1
          raw: "ls -la /"
          changed_when: False
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)

    message = "goodplay_platform 'thename:theversion' specified in inventory for host " \
        "'guesthostname' not found in .goodplay.yml"
    assert message in str(result.getfailures()[0].longrepr)


def test_docker_pull_called_with_resolved_goodplay_platform(testdir, docker_client):
    docker_client.inspect_image.side_effect = \
        docker.errors.NotFound('image not found', None,
                               explanation='simulate missing docker image')

    smart_create(testdir.tmpdir, '''
    ## .goodplay.yml
    platforms:
      - name: thename
        version: theversion
        image: busybox:latest

    ## inventory
    guesthostname goodplay_platform=thename:theversion ansible_user=root

    ## test_playbook.yml
    - hosts: guesthostname
      gather_facts: no
      tasks:
        - name: task 1
          raw: "ls -la /"
          changed_when: False
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)

    docker_client.inspect_image.assert_called_once_with('busybox:latest')
    docker_client.pull.assert_called_once_with('busybox:latest')


def test_started_docker_container_is_removed_after_successful_run(testdir, docker_client):
    smart_create(testdir.tmpdir, '''
    ## inventory
    guesthostname goodplay_image=busybox:latest ansible_user=root

    ## test_playbook.yml
    - hosts: guesthostname
      gather_facts: no
      tasks:
        - name: task 1
          raw: "ls -la /"
          changed_when: False
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)

    assert docker_client.start.call_count == 1

    started_container_id = docker_client.start.call_args[0][0]
    docker_client.remove_container.assert_called_once_with(
        started_container_id, force=True)


def test_started_docker_container_is_removed_after_failed_run(testdir, docker_client):
    smart_create(testdir.tmpdir, '''
    ## inventory
    guesthostname goodplay_image=busybox:latest ansible_user=root

    ## test_playbook.yml
    - hosts: guesthostname
      gather_facts: no
      tasks:
        - name: intentionally failing task
          raw: who
          failed_when: True
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)

    assert docker_client.start.call_count == 1

    started_container_id = docker_client.start.call_args[0][0]
    docker_client.remove_container.assert_called_once_with(
        started_container_id, force=True)


def test_group_vars_directory_beside_inventory_file_is_incorporated(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    guesthostname goodplay_image=busybox:latest ansible_user=root

    ## group_vars/all
    hello: world

    ## test_playbook.yml
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

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


def test_group_vars_directory_beside_inventory_directory_is_incorporated(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory/static
    guesthostname goodplay_image=busybox:latest ansible_user=root

    ## inventory/group_vars/all
    hello: world

    ## test_playbook.yml
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

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


def test_host_vars_directory_beside_inventory_file_is_incorporated(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    guesthostname goodplay_image=busybox:latest ansible_user=root

    ## host_vars/guesthostname
    hello: world

    ## test_playbook.yml
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

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


def test_host_vars_directory_beside_inventory_directory_is_incorporated(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory/static
    guesthostname goodplay_image=busybox:latest ansible_user=root

    ## inventory/host_vars/guesthostname
    hello: world

    ## test_playbook.yml
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

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


def test_role_with_goodplay_platform_wildcard(testdir, docker_client):
    smart_create(testdir.tmpdir, '''
    ## local-role-base/role1/meta/main.yml
    galaxy_info:
      author: John Doe
      platforms:
        - name: EL
          versions:
            - 6
            - 7
    dependencies: []

    ## local-role-base/role1/tasks/main.yml
    - ping:

    ## local-role-base/role1/tests/.goodplay.yml
    platforms:
      - name: EL
        version: 6
        image: centos:centos6

      - name: EL
        version: 7
        image: centos:centos7

    ## local-role-base/role1/tests/inventory
    default goodplay_platform=* ansible_user=root

    ## local-role-base/role1/tests/test_playbook.yml
    - hosts: default
      gather_facts: no
      tasks:
        - name: host is reachable
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=2)

    assert docker_client.create_container.call_count == 2

    _, _, kwargs = docker_client.create_container.mock_calls[0]
    assert kwargs['image'] == 'centos:centos6'

    _, _, kwargs = docker_client.create_container.mock_calls[1]
    assert kwargs['image'] == 'centos:centos7'

    assert docker_client.start.call_count == 2


def test_hosts_without_domain_can_resolve_each_other(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    guesthost1 goodplay_image=busybox:latest ansible_user=root
    guesthost2 goodplay_image=busybox:latest ansible_user=root

    ## test_playbook.yml
    - hosts: guesthost1
      gather_facts: no
      tasks:
        - name: assert guesthost2 is reachable
          raw: ping -c 1 guesthost2
          changed_when: False
          tags: test

    - hosts: guesthost2
      gather_facts: no
      tasks:
        - name: assert guesthost1 is reachable
          raw: ping -c 1 guesthost1
          changed_when: False
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=2)


def test_hosts_with_domain_can_resolve_each_other(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    host1.domain1.tld goodplay_image=busybox:latest ansible_user=root
    host2.domain1.tld goodplay_image=busybox:latest ansible_user=root
    host1.domain2.tld goodplay_image=busybox:latest ansible_user=root

    ## test_playbook.yml
    - hosts: host1.domain1.tld
      gather_facts: no
      tasks:
        # host1.domain1.tld assertions
        - name: assert host1.domain1.tld can be resolved on host1.domain1.tld
          raw: ping -c 1 host1.domain1.tld
          changed_when: False
          tags: test

        - name: assert host1 can be resolved on host1.domain1.tld
          raw: ping -c 1 host1
          changed_when: False
          tags: test

        # host2.domain1.tld assertions
        - name: assert host2.domain1.tld can be resolved on host1.domain1.tld
          raw: ping -c 1 host2.domain1.tld
          changed_when: False
          tags: test

        - name: assert host2 can be resolved on host1.domain1.tld
          raw: ping -c 1 host2
          changed_when: False
          tags: test

        # host1.domain2.tld assertions
        - name: assert host1.domain2.tld can be resolved on host1.domain1.tld
          raw: ping -c 1 host1.domain2.tld
          changed_when: False
          tags: test

    - hosts: host2.domain1.tld
      gather_facts: no
      tasks:
        # host1.domain1.tld assertions
        - name: assert host1.domain1.tld can be resolved on host2.domain1.tld
          raw: ping -c 1 host1.domain1.tld
          changed_when: False
          tags: test

        - name: assert host1 can be resolved on host2.domain1.tld
          raw: ping -c 1 host1
          changed_when: False
          tags: test

        # host2.domain1.tld assertions
        - name: assert host2.domain1.tld can be resolved on host2.domain1.tld
          raw: ping -c 1 host2.domain1.tld
          changed_when: False
          tags: test

        - name: assert host2 can be resolved on host2.domain1.tld
          raw: ping -c 1 host2
          changed_when: False
          tags: test

        # host1.domain2.tld assertions
        - name: assert host1.domain2.tld can be resolved on host2.domain1.tld
          raw: ping -c 1 host1.domain2.tld
          changed_when: False
          tags: test

    - hosts: host1.domain2.tld
      gather_facts: no
      tasks:
        # host1.domain1.tld assertions
        - name: assert host1.domain1.tld can be resolved on host1.domain2.tld
          raw: ping -c 1 host1.domain1.tld
          changed_when: False
          tags: test

        # host2.domain1.tld assertions
        - name: assert host2.domain1.tld can be resolved on host1.domain2.tld
          raw: ping -c 1 host2.domain1.tld
          changed_when: False
          tags: test

        - name: assert host2 cannot be resolved on host1.domain2.tld
          raw: ping -c 1 host2
          register: ping_result
          changed_when: False
          failed_when: "ping_result.rc != 1"
          tags: test

        # host1.domain2.tld assertions
        - name: assert host1.domain2.tld can be resolved on host1.domain2.tld
          raw: ping -c 1 host1.domain2.tld
          changed_when: False
          tags: test

        - name: assert host1 can be resolved on host1.domain2.tld
          raw: ping -c 1 host1
          changed_when: False
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=15)


def test_hosts_can_resolve_google_com_domain(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    guesthost goodplay_image=busybox:latest ansible_user=root

    ## test_playbook.yml
    - hosts: guesthost
      gather_facts: no
      tasks:
        - name: assert google.com domain is reachable
          raw: ping -c 1 google.com
          changed_when: False
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)
