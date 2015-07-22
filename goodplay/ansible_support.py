# -*- coding: utf-8 -*-

import yaml


class AnsibleSupport(object):
    @classmethod
    def is_test_playbook_file(cls, path):
        has_test_prefix = path.basename.startswith('test_')

        return has_test_prefix and cls.is_playbook_file(path)

    @classmethod
    def is_playbook_file(cls, path):
        is_yaml_file = path.ext == '.yml'

        if is_yaml_file:
            yaml_file_content = yaml.safe_load(path.read())
            yaml_file_is_ansible_playbook = \
                isinstance(yaml_file_content, list) \
                and len(yaml_file_content) \
                and isinstance(yaml_file_content[0], dict) \
                and (
                    yaml_file_content[0].get('hosts')
                    or yaml_file_content[0].get('include')
                )

            return yaml_file_is_ansible_playbook

        return False
