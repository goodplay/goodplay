# -*- coding: utf-8 -*-

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
        yaml_file_is_ansible_playbook = \
            isinstance(yaml_file_content, list) \
            and len(yaml_file_content) \
            and isinstance(yaml_file_content[0], dict) \
            and (yaml_file_content[0].get('hosts') or yaml_file_content[0].get('include'))

        return yaml_file_is_ansible_playbook

    return False
