# -*- coding: utf-8 -*-

import pytest

from goodplay_helpers import skip_if_no_docker, smart_create

pytestmark = pytest.mark.integration


@skip_if_no_docker
def test_group_vars_directory_beside_inventory_file_is_incorporated(testdir):
    smart_create(testdir.tmpdir, '''
    ## docker-compose.yml
    version: "2"
    services:
      guesthostname:
        image: "busybox:latest"
        tty: True

    ## inventory
    guesthostname ansible_user=root

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


@skip_if_no_docker
def test_group_vars_directory_beside_inventory_directory_is_incorporated(testdir):
    smart_create(testdir.tmpdir, '''
    ## docker-compose.yml
    version: "2"
    services:
      guesthostname:
        image: "busybox:latest"
        tty: True

    ## inventory/static
    guesthostname ansible_user=root

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


@skip_if_no_docker
def test_host_vars_directory_beside_inventory_file_is_incorporated(testdir):
    smart_create(testdir.tmpdir, '''
    ## docker-compose.yml
    version: "2"
    services:
      guesthostname:
        image: "busybox:latest"
        tty: True

    ## inventory
    guesthostname ansible_user=root

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


@skip_if_no_docker
def test_host_vars_directory_beside_inventory_directory_is_incorporated(testdir):
    smart_create(testdir.tmpdir, '''
    ## docker-compose.yml
    version: "2"
    services:
      guesthostname:
        image: "busybox:latest"
        tty: True

    ## inventory/static
    guesthostname ansible_user=root

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


@skip_if_no_docker
def test_role_with_multiple_environments(testdir):
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

    ## local-role-base/role1/tests/docker-compose.EL.6.yml
    version: "2"
    services:
      default:
        image: "centos:centos6"
        tty: True

    ## local-role-base/role1/tests/docker-compose.EL.7.yml
    version: "2"
    services:
      default:
        image: "centos:centos7"
        tty: True

    ## local-role-base/role1/tests/inventory
    default ansible_user=root

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


@skip_if_no_docker
def test_hosts_without_domain_can_resolve_each_other(testdir):
    smart_create(testdir.tmpdir, '''
    ## docker-compose.yml
    version: "2"
    services:
      guesthost1:
        image: "busybox:latest"
        tty: True

      guesthost2:
        image: "busybox:latest"
        tty: True

    ## inventory
    guesthost1 ansible_user=root
    guesthost2 ansible_user=root

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


@skip_if_no_docker
def test_hosts_with_domain_can_resolve_each_other(testdir):
    smart_create(testdir.tmpdir, '''
    ## docker-compose.yml
    version: "2"
    services:
      host1.domain1.tld:
        image: "busybox:latest"
        tty: True
        domainname: domain1.tld
        hostname: host1
        dns_search:
          - domain1.tld

      host2.domain1.tld:
        image: "busybox:latest"
        tty: True
        domainname: domain1.tld
        hostname: host2
        dns_search:
          - domain1.tld

      host1.domain2.tld:
        image: "busybox:latest"
        tty: True
        domainname: domain2.tld
        hostname: host1
        dns_search:
          - domain2.tld

    ## inventory
    host1.domain1.tld ansible_user=root
    host2.domain1.tld ansible_user=root
    host1.domain2.tld ansible_user=root

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
    result.assertoutcome(passed=14)


@skip_if_no_docker
def test_hosts_can_resolve_google_com_domain(testdir):
    smart_create(testdir.tmpdir, '''
    ## docker-compose.yml
    version: "2"
    services:
      guesthost:
        image: "busybox:latest"
        tty: True

    ## inventory
    guesthost ansible_user=root

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


@skip_if_no_docker
def test_docker_build_error_results_in_fail_with_message(testdir):
    smart_create(testdir.tmpdir, '''
    ## image/Dockerfile
    FROM "https://unknownregistry/busybox:latest"

    ## docker-compose.yml
    version: "2"
    services:
      guesthost:
        build:
          context: "./image"
        tty: True

    ## inventory
    guesthost ansible_user=root

    ## test_playbook.yml
    - hosts: guesthost
      gather_facts: no
      tasks:
        - name: task1
          ping:
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)

    assert "Failed: building service 'guesthost' failed with reason 'invalid reference format'" \
        in str(result.getfailures()[0].longrepr)
