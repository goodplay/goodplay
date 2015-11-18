# -*- coding: utf-8 -*-

import yaml


def get_goodplay_config(playbook_path):
    config_path = find_config_path(playbook_path)

    if config_path:
        return yaml.safe_load(config_path.read())

    return get_default_goodplay_config()


def find_config_path(playbook_path):
    for ancestor_path in playbook_path.parts(reverse=True)[1:]:
        goodplay_yml_path = ancestor_path.join('.goodplay.yml')

        if goodplay_yml_path.check(file=True):
            return goodplay_yml_path


def get_default_goodplay_config():
    return dict(platforms=[])
