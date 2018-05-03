# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

import yaml

from .inventory import Inventory  # noqa: F401
from .playbook import Playbook  # noqa: F401


def is_test_playbook_file(path):
    has_test_prefix = path.basename.startswith('test_')

    return has_test_prefix and is_playbook_file(path)


def is_playbook_file(path):
    is_yaml_file = path.ext == '.yml'

    if is_yaml_file:
        yaml_file_content = yaml.safe_load(path.read())
        yaml_file_is_ansible_playbook = is_playbook_content(yaml_file_content)

        return yaml_file_is_ansible_playbook

    return False


def is_playbook_content(content):
    return isinstance(content, list) \
        and len(content) \
        and isinstance(content[0], dict) \
        and (content[0].get('hosts')
             or content[0].get('include')
             or content[0].get('import_playbook'))
