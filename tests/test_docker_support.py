# -*- coding: utf-8 -*-

from goodplay.docker_support import (
    is_docker_compose_file, config_paths_for_playbook_path, environment_name_for_config_path)

from goodplay_helpers import smart_create


def test_is_docker_compose_file_returns_false_for_non_docker_compose_prefix(tmpdir):
    path = tmpdir.join('docker.yml')
    path.ensure()

    assert not is_docker_compose_file(path)


def test_is_docker_compose_file_returns_false_for_non_yml_suffix(tmpdir):
    path = tmpdir.join('docker-compose.json')
    path.ensure()

    assert not is_docker_compose_file(path)


def test_is_docker_compose_file_returns_false_for_directory(tmpdir):
    path = tmpdir.join('docker-compose.yml')
    path.ensure(dir=True)

    assert not is_docker_compose_file(path)


def test_is_docker_compose_file_returns_false_for_multidot_name(tmpdir):
    path = tmpdir.join('docker-compose..yml')
    path.ensure()

    assert not is_docker_compose_file(path)


def test_is_docker_compose_file_success(tmpdir):
    path = tmpdir.join('docker-compose.yml')
    path.ensure()

    assert is_docker_compose_file(path)


def test_environment_name_for_config_path_empty():
    assert environment_name_for_config_path([]) is None


def test_environment_name_for_config_path_docker_compose_yml_only():
    assert environment_name_for_config_path(['docker-compose.yml']) == ''


def test_environment_name_for_config_path_docker_compose_override_yml_only():
    assert environment_name_for_config_path(['docker-compose.override.yml']) == ''


def test_environment_name_for_config_path_docker_compose_yml_and_override():
    docker_compose_file_group = ['docker-compose.yml', 'docker-compose.override.yml']
    assert environment_name_for_config_path(docker_compose_file_group) == ''


def test_environment_name_for_config_path_single_level():
    docker_compose_file_group = ['docker-compose.yml', 'docker-compose.item1.yml']
    assert environment_name_for_config_path(docker_compose_file_group) == 'item1'


def test_environment_name_for_config_path_muliple_levels():
    docker_compose_file_group = [
        'docker-compose.yml',
        'docker-compose.item1.override.yml',
        'docker-compose.item1.item11.item111.override.yml'
    ]
    expected = 'item1.item11.item111'
    assert environment_name_for_config_path(docker_compose_file_group) == expected


def test_config_paths_for_playbook_path_empty(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')

    assert config_paths_for_playbook_path(playbook_path) == []


def test_config_paths_for_playbook_path_docker_compose_yml_only(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')

    smart_create(tmpdir, '''
    ## docker-compose.yml
    ''')

    expected = [['docker-compose.yml']]
    assert config_paths_for_playbook_path(playbook_path) == expected


def test_config_paths_for_playbook_path_docker_compose_override_yml_only(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')

    smart_create(tmpdir, '''
    ## docker-compose.override.yml
    ''')

    expected = [['docker-compose.override.yml']]
    assert config_paths_for_playbook_path(playbook_path) == expected


def test_config_paths_for_playbook_path_docker_compose_yml_and_override(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')

    smart_create(tmpdir, '''
    ## docker-compose.yml
    ## docker-compose.override.yml
    ''')

    expected = [
        ['docker-compose.yml', 'docker-compose.override.yml']
    ]
    assert config_paths_for_playbook_path(playbook_path) == expected


def test_config_paths_for_playbook_path_single_level(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')

    smart_create(tmpdir, '''
    ## docker-compose.yml
    ## docker-compose.item1.yml
    ## docker-compose.item2.yml
    ''')

    expected = [
        ['docker-compose.item1.yml'],
        ['docker-compose.item2.yml']
    ]
    assert config_paths_for_playbook_path(playbook_path) == expected


def test_config_paths_for_playbook_path_single_level_only_override(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')

    smart_create(tmpdir, '''
    ## docker-compose.yml
    ## docker-compose.item1.override.yml
    ''')

    expected = [
        ['docker-compose.yml', 'docker-compose.item1.override.yml']
    ]
    assert config_paths_for_playbook_path(playbook_path) == expected


def test_config_paths_for_playbook_path_single_level_and_override(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')

    smart_create(tmpdir, '''
    ## docker-compose.yml
    ## docker-compose.item1.yml
    ## docker-compose.item1.override.yml
    ''')

    expected = [
        ['docker-compose.item1.yml', 'docker-compose.item1.override.yml']
    ]
    assert config_paths_for_playbook_path(playbook_path) == expected


def test_config_paths_for_playbook_path_multiple_levels(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')

    smart_create(tmpdir, '''
    ## docker-compose.yml
    ## docker-compose.item1.item11.yml
    ## docker-compose.item2.item21.yml
    ''')

    expected = [
        ['docker-compose.item1.item11.yml'],
        ['docker-compose.item2.item21.yml']
    ]
    assert config_paths_for_playbook_path(playbook_path) == expected


def test_config_paths_for_playbook_path_multiple_levels_and_override(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')

    smart_create(tmpdir, '''
    ## docker-compose.yml
    ## docker-compose.item1.override.yml
    ## docker-compose.item1.item11.item111.override.yml
    ## docker-compose.item2.item21.yml
    ''')

    expected = [
        ['docker-compose.yml', 'docker-compose.item1.override.yml',
         'docker-compose.item1.item11.item111.override.yml'],
        ['docker-compose.item2.item21.yml']
    ]
    assert config_paths_for_playbook_path(playbook_path) == expected
