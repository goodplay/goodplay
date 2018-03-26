# -*- coding: utf-8 -*-

from goodplay.plugin import (
    GoodplayPlaybookFile, GoodplayEnvironment, GoodplayPlaybook, GoodplayTest)


class AttrDict(dict):
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


def test_nodeid_goodplay_playbook_file(tmpdir):
    playbook_path = tmpdir.join('test_playbook.yml')

    config = AttrDict(rootdir=tmpdir)
    session = AttrDict(non='empty', config=config)

    node = GoodplayPlaybookFile(ctx=None, fspath=playbook_path, config=config, session=session)
    assert node.nodeid == 'test_playbook.yml'


def test_nodeid_goodplay_environment_with_no_environment_name_is_same_as_parent(tmpdir):
    parent = AttrDict(
        config=AttrDict(rootdir=tmpdir),
        session=AttrDict(non='empty'),
        fspath=tmpdir.join('test_playbook.yml'),
        nodeid='test_playbook.yml'
    )

    node = GoodplayEnvironment(environment_name=None, parent=parent)
    assert node.nodeid == 'test_playbook.yml'


def test_nodeid_goodplay_environment_with_environment_name_adds_environment_name(tmpdir):
    parent = AttrDict(
        config=AttrDict(rootdir=tmpdir),
        session=AttrDict(non='empty'),
        fspath=tmpdir.join('test_playbook.yml'),
        nodeid='test_playbook.yml'
    )

    node = GoodplayEnvironment(environment_name='ubuntu.trusty', parent=parent)
    assert node.nodeid == 'test_playbook.yml::ubuntu.trusty'


def test_nodeid_goodplay_environment_name_is_same_as_parent(tmpdir):
    parent = AttrDict(
        config=AttrDict(rootdir=tmpdir),
        session=AttrDict(non='empty'),
        fspath=tmpdir.join('test_playbook.yml'),
        nodeid='test_playbook.yml::ubuntu.trusty'
    )

    node = GoodplayPlaybook(name='test_playbook.yml', parent=parent)
    assert node.nodeid == 'test_playbook.yml::ubuntu.trusty'


def test_nodeid_goodplay_test_add_test_name(tmpdir):
    parent = AttrDict(
        config=AttrDict(rootdir=tmpdir),
        session=AttrDict(non='empty'),
        fspath=tmpdir.join('test_playbook.yml'),
        nodeid='test_playbook.yml::ubuntu.trusty'
    )

    task = AttrDict(name='host is reachable')

    node = GoodplayTest(task=task, parent=parent)
    assert node.nodeid == 'test_playbook.yml::ubuntu.trusty::host is reachable'
