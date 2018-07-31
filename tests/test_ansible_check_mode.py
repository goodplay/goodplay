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


def test_command_task_tagged_with_test_runs_in_normal_mode(testdir):
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


def test_shell_task_tagged_with_test_runs_in_normal_mode(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: intentional test with side effect
          shell: touch "{{ playbook_dir }}/HELLO"
          changed_when: False
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)

    assert testdir.tmpdir.join('HELLO').check(file=True)


def test_custom_module_runs_in_normal_mode_when_check_mode_not_supported(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## library/checkrunmode.py
    from ansible.module_utils.basic import AnsibleModule

    import os

    def main():
        module = AnsibleModule(
            argument_spec = dict(),
            supports_check_mode=False
        )

        module.exit_json(changed=False, run_in_check_mode=module.check_mode)

    if __name__ == '__main__':
        main()

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: assert custom module not run in check mode
          checkrunmode:
          register: result
          failed_when: "{{ result.run_in_check_mode }}"
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)


def test_custom_module_runs_in_check_mode_when_supported(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## library/checkrunmode.py
    from ansible.module_utils.basic import AnsibleModule

    import os

    def main():
        module = AnsibleModule(
            argument_spec = dict(),
            supports_check_mode=True
        )

        module.exit_json(changed=False, run_in_check_mode=module.check_mode)

    if __name__ == '__main__':
        main()

    ## test_playbook.yml
    - hosts: 127.0.0.1
      gather_facts: no
      tasks:
        - name: assert custom module run in check mode
          checkrunmode:
          register: result
          failed_when: "{{ not result.run_in_check_mode }}"
          tags: test
    ''')

    result = testdir.inline_run('-s')
    result.assertoutcome(passed=1)
