# -*- coding: utf-8 -*-

from goodplay_helpers import skip_if_no_docker, smart_create


@skip_if_no_docker
def test_become_user_on_task_without_become_does_not_execute_as_become_user(testdir):
    smart_create(testdir.tmpdir, '''
    ## docker-compose.yml
    version: "2"
    services:
      host1:
        image: centos:centos6
        tty: True

    ## inventory
    host1 ansible_user=root

    ## test_playbook.yml
    - hosts: host1
      gather_facts: no
      tasks:
        - name: create system group myservice
          group:
            name: myservice
            system: yes
            state: present

        - name: create system user myservice
          user:
            name: myservice
            group: myservice
            shell: /sbin/nologin
            system: yes
            state: present

        - name: create myservice directory
          file:
            path: /opt/myservice
            owner: myservice
            group: myservice
            mode: 0700
            state: directory

        - name: intentionally only specify become_user on this task
          file:
            path: /opt/myservice/somefile
            state: touch
          become_user: myservice

        - name: ensure somefile is owned by root user which is not the become_user
          file:
            path: /opt/myservice/somefile
            owner: root
            group: root
            state: file
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


@skip_if_no_docker
def test_become_with_become_user_on_play(testdir):
    smart_create(testdir.tmpdir, '''
    ## docker-compose.yml
    version: "2"
    services:
      host1:
        image: centos:centos6
        tty: True

    ## inventory
    host1 ansible_user=root

    ## test_playbook.yml
    - hosts: host1
      gather_facts: no
      become_user: myservice
      tasks:
        - name: create system group myservice
          group:
            name: myservice
            system: yes
            state: present

        - name: create system user myservice
          user:
            name: myservice
            group: myservice
            shell: /sbin/nologin
            system: yes
            state: present

        - name: create myservice directory
          file:
            path: /opt/myservice
            owner: myservice
            group: myservice
            mode: 0700
            state: directory

        - name: make some file operation as myservice user
          file:
            path: /opt/myservice/somefile
            state: touch
          become: yes

        - name: ensure somefile is owned by myservice user
          file:
            path: /opt/myservice/somefile
            owner: myservice
            group: myservice
            state: file
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


@skip_if_no_docker
def test_become_with_become_user_on_task(testdir):
    smart_create(testdir.tmpdir, '''
    ## docker-compose.yml
    version: "2"
    services:
      host1:
        image: centos:centos6
        tty: True

    ## inventory
    host1 ansible_user=root

    ## test_playbook.yml
    - hosts: host1
      gather_facts: no
      tasks:
        - name: create system group myservice
          group:
            name: myservice
            system: yes
            state: present

        - name: create system user myservice
          user:
            name: myservice
            group: myservice
            shell: /sbin/nologin
            system: yes
            state: present

        - name: create myservice directory
          file:
            path: /opt/myservice
            owner: myservice
            group: myservice
            mode: 0700
            state: directory

        - name: make some file operation as myservice user
          file:
            path: /opt/myservice/somefile
            state: touch
          become: yes
          become_user: myservice

        - name: ensure somefile is owned by myservice user
          file:
            path: /opt/myservice/somefile
            owner: myservice
            group: myservice
            state: file
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)
