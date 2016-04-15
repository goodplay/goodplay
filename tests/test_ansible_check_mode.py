# -*- coding: utf-8 -*-

from goodplay_helpers import smart_create


def test_file_task_tagged_with_test_runs_in_check_mode(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - file:
            path: "{{ playbook_dir }}/README"
            state: touch

        - name: intentionally failing test
          file:
            path: "{{ playbook_dir }}/README"
            state: absent
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)

    assert testdir.tmpdir.join('README').check(file=True)


def test_lineinfile_task_tagged_with_test_runs_in_check_mode(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - lineinfile:
            dest: "{{ playbook_dir }}/HELLO"
            create: yes
            line: "WORLD"
            state: present

        - name: intentionally failing test
          file:
            path: "{{ playbook_dir }}/HELLO"
            line: "WORLD"
            state: absent
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)

    assert testdir.tmpdir.join('HELLO').check(file=True)
    assert testdir.tmpdir.join('HELLO').read() == 'WORLD\n'


def test_task_with_always_run_and_tagged_with_test_runs_in_normal_mode(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - file:
            path: "{{ playbook_dir }}/README"
            state: touch

        - name: intentionally failing test
          file:
            path: "{{ playbook_dir }}/README"
            state: absent
          always_run: yes
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(failed=1)

    assert not testdir.tmpdir.join('README').check()


def test_task_tagged_with_test_that_does_not_support_check_mode_runs_in_normal_mode(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: intentional test with side effect
          command: touch "{{ playbook_dir }}/HELLO"
          changed_when: False
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)

    assert testdir.tmpdir.join('HELLO').check(file=True)
