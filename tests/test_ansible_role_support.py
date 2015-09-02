# -*- coding: utf-8 -*-

import subprocess
import yaml


pytest_plugins = 'pytester'


def create_role(
        role_base_path, role_name, test_playbook=None, dependencies=None,
        inventory=None):
    if not dependencies:
        dependencies = []
    if not inventory:
        inventory = '127.0.0.1 ansible_connection=local'

    # ensure some directory other than cwd is used
    # as ansible v2 seems to automatically look for roles in cwd
    role_path = role_base_path.join(role_name)

    # create role meta
    meta_info = {
        'galaxy_info': {
            'author': 'John Doe'
        },
        'dependencies': dependencies,
    }
    role_path.join('meta', 'main.yml').write(yaml.dump(meta_info), ensure=True)

    # create role tasks
    role_path.join('tasks', 'main.yml').write('''---
- file:
    path: "{0!s}"
    state: touch
'''.format(role_path.join('.run')), ensure=True)

    if test_playbook:
        # create role tests
        role_path.join('tests', 'inventory').write(inventory, ensure=True)
        role_path.join('tests', 'test_playbook.yml').write(
            test_playbook, ensure=True)

    # create role git repo
    subprocess.check_call(
        ['git', 'init'], cwd=str(role_path))
    subprocess.check_call(
        ['git', 'config', 'user.name', 'John Doe'], cwd=str(role_path))
    subprocess.check_call(
        ['git', 'config', 'user.email', 'john.doe@acme.com'],
        cwd=str(role_path))
    subprocess.check_call(
        ['git', 'add', '--all'], cwd=str(role_path))
    subprocess.check_call(
        ['git', 'commit', '-m', 'initial commit'], cwd=str(role_path))

    return 'git+file://{0!s}'.format(role_path)


def run(testdir):
    return testdir.inline_run('-s')


def test_passed_on_selfcontained_role(testdir):
    local_role_base_path = testdir.tmpdir.join('local-role-base')

    create_role(local_role_base_path, 'role1', '''---
- hosts: 127.0.0.1
  roles:
    - role: role1

- hosts: 127.0.0.1
  tasks:
    - name: assert role1 run
      file:
        path: "{0!s}"
        state: file
      tags: test
'''.format(local_role_base_path.join('role1', '.run')))

    result = run(testdir)
    assert result.countoutcomes() == [1, 0, 0]


def test_passed_on_role_with_dependent_role_beside(testdir):
    local_role_base_path = testdir.tmpdir.join('local-role-base')

    role1_url = create_role(local_role_base_path, 'role1')

    create_role(local_role_base_path, 'role2', '''---
- hosts: 127.0.0.1
  roles:
    - role: role2

- hosts: 127.0.0.1
  tasks:
    - name: assert role1 run
      file:
        path: "{0!s}"
        state: file
      tags: test

    - name: assert role2 run
      file:
        path: "{1!s}"
        state: file
      tags: test
'''.format(
        local_role_base_path.join('role1', '.run'),
        local_role_base_path.join('role2', '.run')
    ), dependencies=[role1_url])

    result = run(testdir)
    assert result.countoutcomes() == [2, 0, 0]


def test_passed_on_role_with_multi_level_dependent_role_beside(testdir):
    local_role_base_path = testdir.tmpdir.join('local-role-base')

    role1_url = create_role(
        local_role_base_path, 'role1')

    role2_url = create_role(
        local_role_base_path, 'role2', dependencies=[role1_url])

    create_role(local_role_base_path, 'role3', '''---
- hosts: 127.0.0.1
  roles:
    - role: role3

- hosts: 127.0.0.1
  tasks:
    - name: assert role1 run
      file:
        path: "{0!s}"
        state: file
      tags: test

    - name: assert role2 run
      file:
        path: "{1!s}"
        state: file
      tags: test

    - name: assert role3 run
      file:
        path: "{2!s}"
        state: file
      tags: test
'''.format(
        local_role_base_path.join('role1', '.run'),
        local_role_base_path.join('role2', '.run'),
        local_role_base_path.join('role3', '.run')
    ), dependencies=[role2_url])

    result = run(testdir)
    assert result.countoutcomes() == [3, 0, 0]


def test_passed_on_role_with_external_dependent_role(testdir):
    external_role_base_path = testdir.tmpdir.join('external-role-base')
    local_role_base_path = testdir.tmpdir.join('local-role-base')

    role1_url = create_role(external_role_base_path, 'role1')

    create_role(local_role_base_path, 'role2', '''---
- hosts: 127.0.0.1
  roles:
    - role: role2

- hosts: 127.0.0.1
  tasks:
    - name: assert role1 run
      file:
        path: "{0!s}"
        state: file
      tags: test

    - name: assert role2 run
      file:
        path: "{1!s}"
        state: file
      tags: test
'''.format(
        external_role_base_path.join('role1', '.run'),
        local_role_base_path.join('role2', '.run')
    ), dependencies=[role1_url])

    result = run(testdir)
    assert result.countoutcomes() == [2, 0, 0]


def test_passed_on_role_with_multi_level_external_dependent_role(testdir):
    external_role_base_path = testdir.tmpdir.join('external-role-base')
    local_role_base_path = testdir.tmpdir.join('local-role-base')

    role1_url = create_role(
        external_role_base_path, 'role1')

    role2_url = create_role(
        external_role_base_path, 'role2', dependencies=[role1_url])

    create_role(local_role_base_path, 'role3', '''---
- hosts: 127.0.0.1
  roles:
    - role: role3

- hosts: 127.0.0.1
  tasks:
    - name: assert role1 run
      file:
        path: "{0!s}"
        state: file
      tags: test

    - name: assert role2 run
      file:
        path: "{1!s}"
        state: file
      tags: test

    - name: assert role3 run
      file:
        path: "{2!s}"
        state: file
      tags: test
'''.format(
        external_role_base_path.join('role1', '.run'),
        external_role_base_path.join('role2', '.run'),
        local_role_base_path.join('role3', '.run')
    ), dependencies=[role2_url])

    result = run(testdir)
    assert result.countoutcomes() == [3, 0, 0]


def test_failed_on_unresolvable_role(testdir):
    local_role_base_path = testdir.tmpdir.join('local-role-base')

    create_role(local_role_base_path, 'role1', '''---
- hosts: 127.0.0.1
  roles:
    - role: role2

- hosts: 127.0.0.1
  tasks:
    - name: task1
      ping:
      tags: test
''')

    result = run(testdir)
    assert result.countoutcomes() == [0, 0, 1]
