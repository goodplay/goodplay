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
    ],
    ids=[
        'hosts',
        'include',
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
