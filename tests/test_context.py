# -*- coding: utf-8 -*-

from goodplay.ansible_support import Inventory, Playbook
from goodplay.context import GoodplayContext


# inventory_path

def test_inventory_path_file_found_in_playbook_path_dir(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    inventory_path = tmpdir.join('inventory')
    inventory_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.inventory_path == inventory_path


def test_inventory_path_dir_found_in_playbook_path_dir(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    inventory_path = tmpdir.join('inventory')
    inventory_path.ensure(dir=True)

    ctx = GoodplayContext(playbook_path)

    assert ctx.inventory_path == inventory_path


def test_inventory_path_is_none_when_not_in_playbook_path_dir(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.inventory_path is None


def test_inventory_path_is_none_when_inventory_path_in_parent_dir(tmpdir):
    playbook_path = tmpdir.join('parent_dir', 'test_playbook.yml')
    playbook_path.ensure()

    inventory_path = tmpdir.join('inventory')
    inventory_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.inventory_path is None


def test_inventory_path_is_none_when_inventory_path_in_sub_dir(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    inventory_path = tmpdir.join('sub_dir', 'inventory')
    inventory_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.inventory_path is None


def test_inventory_path_is_cached(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    inventory_path = tmpdir.join('inventory')
    inventory_path.ensure()

    ctx = GoodplayContext(playbook_path)

    first_result = ctx.inventory_path
    assert first_result is not None
    assert id(ctx.inventory_path) == id(first_result)


# inventory

def test_inventory_is_none_when_inventory_path_is_none(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)
    ctx.inventory_path = None

    assert ctx.inventory is None


def test_inventory_class(tmpdir):
    inventory_path = tmpdir.join('inventory')
    inventory_path.write('host1', ensure=True)

    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.inventory.__class__ == Inventory


def test_inventory_is_cached(tmpdir):
    inventory_path = tmpdir.join('inventory')
    inventory_path.write('host1', ensure=True)

    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    first_result = ctx.inventory
    assert first_result is not None
    assert id(ctx.inventory) == id(first_result)


# playbook_dir_path

def test_playbook_dir_path_is_playbook_path_directory(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.playbook_dir_path == tmpdir


def test_playbook_dir_path_is_cached(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    first_result = ctx.playbook_dir_path
    assert first_result is not None
    assert id(ctx.playbook_dir_path) == id(first_result)


# playbook

def test_playbook_is_none_when_inventory_path_is_none(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)
    ctx.inventory_path = None

    assert ctx.playbook is None


def test_playbook_class(tmpdir):
    inventory_path = tmpdir.join('inventory')
    inventory_path.write('host1', ensure=True)

    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.write('''---
- hosts: host1
  tasks:
    - name: task 1
      ping:
      tags: test
''', ensure=True)

    ctx = GoodplayContext(playbook_path)

    assert ctx.playbook.__class__ == Playbook


def test_playbook_is_cached(tmpdir):
    inventory_path = tmpdir.join('inventory')
    inventory_path.write('host1', ensure=True)

    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.write('''---
- hosts: host1
  tasks:
    - name: task 1
      ping:
      tags: test
''', ensure=True)

    ctx = GoodplayContext(playbook_path)

    first_result = ctx.playbook
    assert first_result is not None
    assert id(ctx.playbook) == id(first_result)


# role_path

def test_role_path_is_none_when_plain_test_playbook(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.role_path is None


def test_role_path_is_none_when_tests_parent_dir_only(tmpdir):
    playbook_path = tmpdir.join('tests', 'test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.role_path is None


def test_role_path_is_none_when_meta_dir_beside_tests_parent_dir_only(tmpdir):
    tmpdir.join('meta').ensure(dir=True)

    playbook_path = tmpdir.join('tests', 'test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.role_path is None


def test_role_path_is_none_when_meta_dir_with_main_yml_dir_beside_tests_parent_dir(tmpdir):
    tmpdir.join('meta', 'main.yml').ensure(dir=True)

    playbook_path = tmpdir.join('tests', 'test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.role_path is None


def test_role_path_is_none_when_meta_dir_with_main_yml_file_beside_playbook_path_dir(tmpdir):
    tmpdir.join('meta', 'main.yml').ensure()

    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.role_path is None


def test_role_path_when_meta_dir_with_main_yml_file_beside_tests_parent_dir(tmpdir):
    tmpdir.join('meta', 'main.yml').ensure()

    playbook_path = tmpdir.join('tests', 'test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.role_path == tmpdir


def test_role_path_when_meta_dir_with_main_yml_file_beside_tests_ancestor_dir(tmpdir):
    tmpdir.join('meta', 'main.yml').ensure()

    playbook_path = tmpdir.join('tests', 'sub_dir1', 'sub_dir2', 'test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.role_path == tmpdir


def test_role_path_is_cached(tmpdir):
    tmpdir.join('meta', 'main.yml').ensure()

    playbook_path = tmpdir.join('tests', 'test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    first_result = ctx.role_path
    assert first_result is not None
    assert id(ctx.role_path) == id(first_result)


# is_role_playbook

def test_is_role_playbook_is_false_when_role_path_is_none(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)
    ctx.role_path = None

    assert ctx.is_role_playbook is False


def test_is_role_playbook_is_true_when_role_path_is_not_none(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)
    ctx.role_path = tmpdir

    assert ctx.is_role_playbook is True


# compose_project_name

def test_compose_project_name_is_same_for_playbook_path_and_environment(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.compose_project_name('env1') == ctx.compose_project_name('env1')


def test_compose_project_name_incorporates_node_id(tmpdir, monkeypatch):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    compose_project_name1 = ctx.compose_project_name('env1')

    monkeypatch.setattr('uuid.getnode', lambda: 1234)

    compose_project_name2 = ctx.compose_project_name('env1')

    assert compose_project_name1 != compose_project_name2


def test_compose_project_name_incorporates_playbook_path(tmpdir):
    playbook_path1 = tmpdir.join('dir1', 'test_playbook.yml')
    playbook_path1.ensure()

    playbook_path2 = tmpdir.join('dir2', 'test_playbook.yml')
    playbook_path2.ensure()

    ctx1 = GoodplayContext(playbook_path1)
    ctx2 = GoodplayContext(playbook_path2)

    assert ctx1.compose_project_name('env1') != ctx2.compose_project_name('env1')


def test_compose_project_name_incorporates_environment(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.compose_project_name('env1') != ctx.compose_project_name('env2')


# release

def test_release_removes_temp_dir_paths(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)
    temp_dir_path = ctx._create_temp_dir_path()

    assert temp_dir_path.check(dir=True)
    assert len(ctx._temp_dir_paths) == 1

    ctx.release()

    assert not temp_dir_path.check()
    assert len(ctx._temp_dir_paths) == 0
