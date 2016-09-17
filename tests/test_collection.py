# -*- coding: utf-8 -*-

from goodplay_helpers import smart_create


def test_ansible_error_message_is_forwarded(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - name: task1
          unknownmodule:
          tags: test
    ''')

    _, result = testdir.inline_genitems()
    result.assertoutcome(failed=1)

    assert result.getfailures()[0].__class__.__name__ == 'CollectReport'

    assert 'ERROR! no action detected in task' \
        in str(result.getfailures()[0].longrepr)


def test_nothing_collected_when_inventory_missing(testdir):
    smart_create(testdir.tmpdir, '''
    ## test_playbook.yml
    - hosts: all
      tasks:
        - name: task1
          ping:
          tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 0


def test_nothing_collected_when_only_non_test_tags(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - name: task1
          ping:
          tags: other
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 0


def test_fail_on_non_unique_task_names_both_tagged_test(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - name: task1
          ping:
          tags: test

        - name: task1
          ping:
          tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome(failed=1)

    message = "ValueError: Playbook '{0!s}' contains tests with non-unique name 'task1'".format(
        testdir.tmpdir.join('test_playbook.yml'))
    assert message in str(result.getfailures()[0].longrepr)
    assert len(items) == 0


def test_pass_on_non_unique_task_names_single_one_tagged_test(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - name: task1
          ping:

        - name: task1
          ping:
          tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 1
    assert items[0].name == 'task1'


def test_pass_on_tagged_test_with_additional_tags(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - name: task1
          ping:
          tags:
            - other1
            - test
            - other2
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 1
    assert items[0].name == 'task1'


def test_single_play_no_tests(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - name: task1
          ping:
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 0


def test_single_play_single_test(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - name: task1
          ping:
          tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 1
    assert items[0].name == 'task1'


def test_single_play_multiple_tests(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - name: task1
          ping:
          tags: test

        - name: task2
          ping:
          tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 2
    assert items[0].name == 'task1'
    assert items[1].name == 'task2'


def test_multiple_plays_no_tests(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - name: task1
          ping:

    - hosts: 127.0.0.1
      tasks:
        - name: task2
          ping:
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 0


def test_multiple_plays_single_test(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - name: task1
          ping:

    - hosts: 127.0.0.1
      tasks:
        - name: task2
          ping:
          tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 1
    assert items[0].name == 'task2'


def test_multiple_plays_multiple_tests(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - name: task1
          ping:
          tags: test

        - name: task2
          ping:

    - hosts: 127.0.0.1
      tasks:
        - name: task3
          ping:

        - name: task4
          ping:
          tags: test

        - name: task5
          ping:
          tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 3
    assert items[0].name == 'task1'
    assert items[1].name == 'task4'
    assert items[2].name == 'task5'


# ansible block support

def test_single_play_single_block_no_tests(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task1
              ping:
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 0


def test_single_play_single_block_single_test(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task1
              ping:
              tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 1
    assert items[0].name == 'task1'


def test_single_play_single_block_multiple_tests(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task1
              ping:
              tags: test

            - name: task2
              ping:
              tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 2
    assert items[0].name == 'task1'
    assert items[1].name == 'task2'


def test_single_play_multiple_blocks_no_tests(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task1
              ping:

        - block:
            - name: task2
              ping:
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 0


def test_single_play_multiple_blocks_single_test(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task1
              ping:

        - block:
            - name: task2
              ping:
              tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 1
    assert items[0].name == 'task2'


def test_single_play_multiple_blocks_multiple_tests(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task1
              ping:
              tags: test

            - name: task2
              ping:

        - block:
            - name: task3
              ping:
              tags: test

            - name: task4
              ping:
              tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 3
    assert items[0].name == 'task1'
    assert items[1].name == 'task3'
    assert items[2].name == 'task4'


def test_multiple_plays_single_block_no_tests(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task1
              ping:

    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task2
              ping:
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 0


def test_multiple_plays_single_block_single_test(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task1
              ping:

    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task2
              ping:
              tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 1
    assert items[0].name == 'task2'


def test_multiple_plays_single_block_multiple_tests(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task1
              ping:

            - name: task2
              ping:
              tags: test

    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task3
              ping:

            - name: task4
              ping:
              tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 2
    assert items[0].name == 'task2'
    assert items[1].name == 'task4'


def test_multiple_plays_multiple_blocks_no_tests(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task1
              ping:

        - block:
            - name: task2
              ping:

    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task3
              ping:

        - block:
            - name: task4
              ping:
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 0


def test_multiple_plays_multiple_blocks_single_test(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task1
              ping:

        - block:
            - name: task2
              ping:

    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task3
              ping:

        - block:
            - name: task4
              ping:
              tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 1
    assert items[0].name == 'task4'


def test_multiple_plays_multiple_blocks_multiple_tests(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task1
              ping:
              tags: test

            - name: task2
              ping:

        - block:
            - name: task3
              ping:
              tags: test

            - name: task4
              ping:
              tags: test

    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task5
              ping:
              tags: test

        - block:
            - name: task6
              ping:
              tags: test

            - name: task7
              ping:
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 5
    assert [item.name for item in items] == ['task1', 'task3', 'task4', 'task5', 'task6']


def test_ignore_test_tasks_in_rescue_block(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task1
              ping:
          rescue:
            - name: task2
              ping:
              tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 0


def test_ignore_test_tasks_in_always_block(testdir):
    smart_create(testdir.tmpdir, '''
    ## inventory
    127.0.0.1 ansible_connection=local

    ## test_playbook.yml
    - hosts: 127.0.0.1
      tasks:
        - block:
            - name: task1
              ping:
          rescue:
            - name: task2
              ping:
          always:
            - name: task3
              ping:
              tags: test
    ''')

    items, result = testdir.inline_genitems()
    result.assertoutcome()
    assert len(items) == 0
