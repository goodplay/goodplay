# -*- coding: utf-8 -*-

from goodplay import config


def test_find_config_path_missing(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml').ensure(file=True)

    assert config.find_config_path(playbook_path) is None


def test_find_config_path_does_not_match_file_with_long_yaml_extension(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml').ensure(file=True)
    tmpdir.join('.goodplay.yaml').ensure(file=True)

    assert config.find_config_path(playbook_path) is None


def test_find_config_path_does_not_match_directory(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml').ensure(file=True)
    tmpdir.join('.goodplay.yml').ensure(dir=True)

    assert config.find_config_path(playbook_path) is None


def test_find_config_path_beside_playbook_path(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml').ensure(file=True)
    expected_config_path = tmpdir.join('.goodplay.yml').ensure(file=True)

    assert config.find_config_path(playbook_path) == expected_config_path


def test_find_config_path_in_playbook_path_direct_ancestor_dir(tmpdir):
    playbook_path = tmpdir.join('dir1', 'test_playbook.yml').ensure(file=True)
    expected_config_path = tmpdir.join('.goodplay.yml').ensure(file=True)

    assert config.find_config_path(playbook_path) == expected_config_path


def test_find_config_path_in_playbook_path_some_ancestor_dir(tmpdir):
    playbook_path = tmpdir.join(
        'dir1', 'dir2', 'dir3', 'test_playbook.yml').ensure(file=True)
    expected_config_path = tmpdir.join('.goodplay.yml').ensure(file=True)

    assert config.find_config_path(playbook_path) == expected_config_path


def test_find_config_path_uses_depth_first(tmpdir):
    playbook_path = tmpdir.join(
        'dir1', 'dir2', 'dir3', 'test_playbook.yml').ensure(file=True)

    # intentionally created config file which should not be matched
    tmpdir.join('dir1', '.goodplay.yml').ensure(file=True)

    expected_config_path = tmpdir.join(
        'dir1', 'dir2', '.goodplay.yml').ensure(file=True)

    assert config.find_config_path(playbook_path) == expected_config_path


def test_get_goodplay_config_defaults(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml').ensure(file=True)

    cfg = config.get_goodplay_config(playbook_path)

    assert isinstance(cfg, dict)
    assert cfg.get('platforms') == []


def test_get_goodplay_config(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml').ensure(file=True)

    tmpdir.join('.goodplay.yml').write('''---
platforms:
  - name: EL
    version: 7
    image: centos:centos7
''', ensure=True)

    cfg = config.get_goodplay_config(playbook_path)

    assert isinstance(cfg, dict)
    assert isinstance(cfg['platforms'], list)
    assert cfg['platforms'] == [
        dict(name='EL', version=7, image='centos:centos7')]
