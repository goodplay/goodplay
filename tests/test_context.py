# -*- coding: utf-8 -*-

from goodplay.ansible_support import Inventory, Playbook
from goodplay.context import GoodplayContext, Platform, PlatformManager


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


# role_meta_info

def test_role_meta_info_reads_meta_dir_main_yml_file(tmpdir):
    tmpdir.join('meta', 'main.yml').write('''---
hello: world
''', ensure=True)

    playbook_path = tmpdir.join('tests', 'test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    assert ctx.role_meta_info == dict(hello='world')


def test_role_meta_info_is_cached(tmpdir):
    tmpdir.join('meta', 'main.yml').write('''---
galaxy_info:
''', ensure=True)

    playbook_path = tmpdir.join('tests', 'test_playbook.yml')
    playbook_path.ensure()

    ctx = GoodplayContext(playbook_path)

    first_result = ctx.role_meta_info
    assert first_result is not None
    assert id(ctx.role_meta_info) == id(first_result)


# platform

def test_platform_base_attributes():
    platform = Platform(name='ubuntu', version='trusty')

    assert platform.name == 'ubuntu'
    assert platform.version == 'trusty'


def test_platform_equal():
    platform1 = Platform(name='ubuntu', version='trusty')
    platform2 = Platform(name='ubuntu', version='trusty')

    assert platform1 == platform2
    assert not platform1 != platform2


def test_platform_version_int_and_string_are_comparable():
    platform1 = Platform(name='EL', version=6)
    platform2 = Platform(name='EL', version='6')

    assert platform1 == platform2
    assert not platform1 != platform2


def test_platform_equal_with_different_kwargs():
    platform1 = Platform(name='ubuntu', version='trusty')
    platform2 = Platform(name='ubuntu', version='trusty', some_param=1234)

    assert platform1 == platform2
    assert not platform1 != platform2


# platform manager

def test_platform_manager_find_by_id_found():
    available_platform = Platform('ubuntu', 'trusty')
    available_platforms = [available_platform]
    platform_manager = PlatformManager(available_platforms)

    assert id(platform_manager.find_by_id('ubuntu:trusty')) == id(available_platform)


def test_platform_manager_find_by_id_not_found():
    available_platform = Platform('ubuntu', 'trusty')
    available_platforms = [available_platform]
    platform_manager = PlatformManager(available_platforms)

    assert platform_manager.find_by_id('ubuntu:precise') is None


def test_platform_manager_find_by_id_without_colon():
    available_platform = Platform('ubuntu', 'trusty')
    available_platforms = [available_platform]
    platform_manager = PlatformManager(available_platforms)

    assert platform_manager.find_by_id('ubuntutrusty') is None


def test_platform_manager_find_by_name_and_version_found():
    available_platform = Platform('ubuntu', 'trusty')
    available_platforms = [available_platform]
    platform_manager = PlatformManager(available_platforms)

    found_platform = platform_manager.find_by_name_and_version('ubuntu', 'trusty')
    assert id(found_platform) == id(available_platform)


def test_platform_manager_find_by_name_and_version_not_found():
    available_platform = Platform('ubuntu', 'trusty')
    available_platforms = [available_platform]
    platform_manager = PlatformManager(available_platforms)

    assert platform_manager.find_by_name_and_version('ubuntu', 'precise') is None


def test_platform_manager_selected_platforms_initial_empty():
    available_platforms = [Platform('ubuntu', 'trusty')]
    platform_manager = PlatformManager(available_platforms)

    assert len(platform_manager.selected_platforms) == 0


def test_platform_manager_select_platform_by_name_and_version_adds_platform_to_selected():
    available_platform = Platform('ubuntu', 'trusty')
    available_platforms = [available_platform]
    platform_manager = PlatformManager(available_platforms)

    assert len(platform_manager.selected_platforms) == 0

    platform_manager.select_platform_by_name_and_version('ubuntu', 'trusty')

    assert len(platform_manager.selected_platforms) == 1
    assert id(platform_manager.selected_platforms[0]) == id(available_platform)


def test_platform_manager_select_platform_by_name_and_version_ignores_already_selected():
    available_platform = Platform('ubuntu', 'trusty')
    available_platforms = [available_platform]
    platform_manager = PlatformManager(available_platforms)

    assert len(platform_manager.selected_platforms) == 0

    platform_manager.select_platform_by_name_and_version('ubuntu', 'trusty')
    platform_manager.select_platform_by_name_and_version('ubuntu', 'trusty')

    assert len(platform_manager.selected_platforms) == 1
    assert id(platform_manager.selected_platforms[0]) == id(available_platform)


def test_platform_manager_select_platform_by_name_and_version_ignores_non_available():
    available_platforms = [Platform('ubuntu', 'trusty')]
    platform_manager = PlatformManager(available_platforms)

    assert len(platform_manager.selected_platforms) == 0

    platform_manager.select_platform_by_name_and_version('ubuntu', 'precise')

    assert len(platform_manager.selected_platforms) == 0
