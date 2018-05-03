# -*- coding: utf-8 -*-

import pytest

from goodplay import ansible_support


# fixtures

@pytest.fixture
def valid_playbook_extension():
    return 'yml'


@pytest.fixture
def invalid_playbook_extension():
    return 'txt'


@pytest.fixture
def valid_test_playbook():
    return '''---
- hosts: default
  tasks:
    - name: host is reachable
      ping:
      tags: test
'''


@pytest.fixture(
    params=[
        '- hosts: default',
        '- include: abc',
        '- import_playbook: otherplaybook.yml',
    ],
    ids=[
        'hosts',
        'include',
        'import_playbook',
    ]
)
def valid_test_playbook_content(request):
    return request.param


@pytest.fixture(
    params=[
        '',
        'string',
        'key: value',
        '[]',
        '- hello world',
        '- key: value',
    ],
    ids=[
        'empty',
        'string',
        'dict',
        'empty-list',
        'non-dict-list',
        'non-play-dict-list',
    ]
)
def invalid_test_playbook_content(request):
    return request.param


# tests

# prefix tests

def test_is_test_playbook_file_with_valid_prefix(
        tmpdir, valid_test_playbook):
    path = tmpdir.join('test_playbook.yml')
    path.write(valid_test_playbook)

    assert ansible_support.is_test_playbook_file(path)


def test_is_test_playbook_file_with_invalid_prefix(
        tmpdir, valid_test_playbook):
    path = tmpdir.join('playbook.yml')
    path.write(valid_test_playbook)

    assert not ansible_support.is_test_playbook_file(path)


# extension tests

def test_is_test_playbook_file_with_valid_extension(
        tmpdir, valid_playbook_extension, valid_test_playbook):
    path = tmpdir.join('test_playbook.' + valid_playbook_extension)
    path.write(valid_test_playbook)

    assert ansible_support.is_test_playbook_file(path)


def test_is_test_playbook_file_with_invalid_extension(
        tmpdir, invalid_playbook_extension, valid_test_playbook):
    path = tmpdir.join('test_playbook.' + invalid_playbook_extension)
    path.write(valid_test_playbook)

    assert not ansible_support.is_test_playbook_file(path)


# content tests

def test_is_test_playbook_file_with_valid_content(
        tmpdir, valid_test_playbook_content):
    path = tmpdir.join('test_playbook.yml')
    path.write(valid_test_playbook_content)

    assert ansible_support.is_test_playbook_file(path)


def test_is_test_playbook_file_with_invalid_content(
        tmpdir, invalid_test_playbook_content):
    path = tmpdir.join('test_playbook.yml')
    path.write(invalid_test_playbook_content)

    assert not ansible_support.is_test_playbook_file(path)


def test_host_vars_are_not_mixed_when_using_multiple_inventories(tmpdir):
    inventory1_path = tmpdir.join('inventory1')
    inventory1_path.write('default key=value1')

    inventory2_path = tmpdir.join('inventory2')
    inventory2_path.write('default key=value2')

    inventory1 = ansible_support.Inventory(inventory1_path)
    inventory2 = ansible_support.Inventory(inventory2_path)

    inventory1_hosts = inventory1.hosts()
    inventory2_hosts = inventory2.hosts()

    assert len(inventory1_hosts) == 1
    assert inventory1_hosts[0].vars()['key'] == 'value1'

    assert len(inventory2_hosts) == 1
    assert inventory2_hosts[0].vars()['key'] == 'value2'
