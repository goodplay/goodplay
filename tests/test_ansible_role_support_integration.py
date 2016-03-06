# -*- coding: utf-8 -*-

import tarfile

import pytest
import yaml

pytestmark = pytest.mark.integration
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
        'dependencies': ansible_role_dependencies(dependencies),
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

    archive_path = role_base_path.join(role_name + '.tar.gz')
    with tarfile.open(str(archive_path), 'w:gz') as tar:
        tar.add(str(role_path), arcname=role_path.basename)

    return str(archive_path)


def ansible_role_dependencies(dependencies):
    return [dict(name=dependency.split('/')[-1][:-7], src=dependency)
            for dependency in dependencies]


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
    result.assertoutcome(passed=1)


def test_failed_on_selfcontained_role_without_meta(testdir):
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

    local_role_base_path.join('role1', 'meta').remove(rec=1)

    result = run(testdir)
    result.assertoutcome(failed=1)


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
    result.assertoutcome(passed=2)


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
    result.assertoutcome(passed=3)


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
    result.assertoutcome(passed=2)


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
    result.assertoutcome(passed=3)


def test_passed_on_role_with_external_soft_dependent_role(testdir):
    external_role_base_path = testdir.tmpdir.join('external-role-base')
    local_role_base_path = testdir.tmpdir.join('local-role-base')

    role1_url = create_role(external_role_base_path, 'role1')

    create_role(local_role_base_path, 'role2', '''---
- hosts: 127.0.0.1
  roles:
    - role: role1
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
    ), dependencies=[])

    local_role_base_path.join('role2', 'tests', 'requirements.yml').write('''---
- name: role1
  src: "{0!s}"
'''.format(role1_url), ensure=True)

    result = run(testdir)
    result.assertoutcome(passed=2)


def test_passed_on_role_with_multi_level_external_soft_dependent_role(testdir):
    external_role_base_path = testdir.tmpdir.join('external-role-base')
    local_role_base_path = testdir.tmpdir.join('local-role-base')

    role1_url = create_role(
        external_role_base_path, 'role1')

    role2_url = create_role(
        external_role_base_path, 'role2', dependencies=[role1_url])

    create_role(local_role_base_path, 'role3', '''---
- hosts: 127.0.0.1
  roles:
    - role: role2
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
    ), dependencies=[])

    local_role_base_path.join('role3', 'tests', 'requirements.yml').write('''---
- name: role2
  src: "{0!s}"
'''.format(role2_url), ensure=True)

    result = run(testdir)
    result.assertoutcome(passed=3)


def test_dependency_beside_takes_precedence_over_soft_dependency(testdir):
    external_role_base_path = testdir.tmpdir.join('external-role-base')
    local_role_base_path = testdir.tmpdir.join('local-role-base')

    create_role(local_role_base_path, 'role1')
    role1soft_url = create_role(external_role_base_path, 'role1soft')

    create_role(local_role_base_path, 'role2', '''---
- hosts: 127.0.0.1
  roles:
    - role: role1
    - role: role2

- hosts: 127.0.0.1
  tasks:
    - name: assert role1 run
      file:
        path: "{0!s}"
        state: file
      tags: test

    - name: assert role1soft not run
      file:
        path: "{1!s}"
        state: absent
      tags: test

    - name: assert role2 run
      file:
        path: "{2!s}"
        state: file
      tags: test
'''.format(
        local_role_base_path.join('role1', '.run'),
        external_role_base_path.join('role1soft', '.run'),
        local_role_base_path.join('role2', '.run')
    ), dependencies=[])

    local_role_base_path.join('role2', 'tests', 'requirements.yml').write('''---
- name: role1
  src: "{0!s}"
'''.format(role1soft_url), ensure=True)

    result = run(testdir)
    result.assertoutcome(passed=3)


def test_dependency_beside_takes_precedence_over_role_dependency(testdir):
    external_role_base_path = testdir.tmpdir.join('external-role-base')
    local_role_base_path = testdir.tmpdir.join('local-role-base')

    create_role(local_role_base_path, 'role1')
    role1external_url = create_role(external_role_base_path, 'role1')

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

    - name: assert role1external not run
      file:
        path: "{1!s}"
        state: absent
      tags: test

    - name: assert role2 run
      file:
        path: "{2!s}"
        state: file
      tags: test
'''.format(
        local_role_base_path.join('role1', '.run'),
        external_role_base_path.join('role1', '.run'),
        local_role_base_path.join('role2', '.run')
    ), dependencies=[role1external_url])

    result = run(testdir)
    result.assertoutcome(passed=3)


def test_soft_dependency_takes_precedence_over_role_dependency(testdir):
    external_role_base_path = testdir.tmpdir.join('external-role-base')
    local_role_base_path = testdir.tmpdir.join('local-role-base')

    role1_url = create_role(external_role_base_path, 'role1')
    role1soft_url = create_role(external_role_base_path, 'role1soft')

    create_role(local_role_base_path, 'role2', '''---
- hosts: 127.0.0.1
  roles:
    - role: role1
    - role: role2

- hosts: 127.0.0.1
  tasks:
    - name: assert role1 not run
      file:
        path: "{0!s}"
        state: absent
      tags: test

    - name: assert role1soft run
      file:
        path: "{1!s}"
        state: file
      tags: test

    - name: assert role2 run
      file:
        path: "{2!s}"
        state: file
      tags: test
'''.format(
        external_role_base_path.join('role1', '.run'),
        external_role_base_path.join('role1soft', '.run'),
        local_role_base_path.join('role2', '.run')
    ), dependencies=[role1_url])

    local_role_base_path.join('role2', 'tests', 'requirements.yml').write('''---
- name: role1
  src: "{0!s}"
'''.format(role1soft_url), ensure=True)

    result = run(testdir)
    result.assertoutcome(passed=3)


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
    result.assertoutcome(failed=1)


def test_ansible_path_is_considered_when_use_local_roles_enabled(testdir, monkeypatch):
    some_ansible_roles_path = testdir.tmpdir.join('some', 'ansible', 'roles')
    some_ansible_roles_path.ensure(dir=True)
    monkeypatch.setattr('ansible.constants.DEFAULT_ROLES_PATH', str(some_ansible_roles_path))

    local_role1_path = some_ansible_roles_path.join('role1')
    local_role1_path.join('tasks', 'main.yml').write('''---
- file:
    path: "{0!s}"
    state: touch
'''.format(local_role1_path.join('.run')), ensure=True)

    role2_path = testdir.tmpdir.join('role2')
    role2_path.join('meta', 'main.yml').write('''---
galaxy_info:
  author: John Doe
dependencies:
  - role1
''', ensure=True)

    role2_path.join('tasks', 'main.yml').write('''---
- ping:
''', ensure=True)

    role2_path.join('tests', 'inventory').write('127.0.0.1 ansible_connection=local', ensure=True)
    role2_path.join('tests', 'test_role2.yml').write('''---
- hosts: 127.0.0.1
  gather_facts: no

  roles:
    - role: role2

- hosts: 127.0.0.1
  gather_facts: no

  tasks:
    - name: assert role1 run
      file:
        path: "{0!s}"
        state: file
      tags: test
'''.format(local_role1_path.join('.run')), ensure=True)

    result = testdir.inline_run('-s', '--use-local-roles')
    result.assertoutcome(passed=1)
