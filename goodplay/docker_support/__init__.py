# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

from cached_property import cached_property
from compose.cli.command import get_project
from compose.service import BuildError
from pytest import fail


def is_docker_compose_file(path):
    is_file = path.check(file=True)
    uses_docker_compose_naming = (
        path.basename.startswith('docker-compose.') and
        path.basename.endswith('.yml') and
        '..' not in path.basename)

    return is_file and uses_docker_compose_naming


def config_name_self_and_above(config_name, suffix=None):
    splitted_config_name = config_name.split('.')
    prefix = [splitted_config_name[0]]
    if not suffix:
        suffix = [splitted_config_name[-1]]
    environment_parts = splitted_config_name[1:-1]

    if environment_parts and environment_parts[-1] == 'override':
        environment_parts.pop()

    while environment_parts:
        yield '.'.join(prefix + environment_parts + suffix)
        environment_parts.pop()

    yield '.'.join(prefix + environment_parts + suffix)


def environment_names_for_playbook_path(playbook_path):
    return [environment_name_for_config_path(config_path)
            for config_path in config_paths_for_playbook_path(playbook_path)]


def config_path_for_environment_name(playbook_path, environment_name):
    for config_path in config_paths_for_playbook_path(playbook_path):
        if environment_name_for_config_path(config_path) == environment_name:
            return config_path


def config_paths_for_playbook_path(playbook_path):  # noqa: R701
    base_path = playbook_path.dirpath()

    # get relative config names sorted descending by len
    config_names = [path.relto(base_path) for path in base_path.listdir(is_docker_compose_file)]
    config_names.sort()
    config_names.sort(key=len, reverse=True)

    config_names_set = set(config_names)

    config_paths = []
    already_visited = set()

    for config_name in config_names:
        if config_name in already_visited:
            continue

        config_path = []
        continue_adding_config_paths = True

        for potential_config_override_name, potential_config_name in zip(
                config_name_self_and_above(config_name, suffix=['override', 'yml']),
                config_name_self_and_above(config_name)):
            if continue_adding_config_paths and potential_config_override_name in config_names_set:
                config_path.insert(0, potential_config_override_name)
            if continue_adding_config_paths and potential_config_name in config_names_set:
                continue_adding_config_paths = False
                config_path.insert(0, potential_config_name)

            already_visited.add(potential_config_override_name)
            already_visited.add(potential_config_name)

        config_paths.append(config_path)

    return config_paths


def environment_name_for_config_path(config_path):
    if config_path:
        environment_parts = config_path[-1].split('.')[1:-1]

        if environment_parts and environment_parts[-1] == 'override':
            environment_parts.pop()

        return '.'.join(environment_parts)


class DockerRunner(object):
    def __init__(self, ctx, environment_name=None):
        self.ctx = ctx
        self.environment_name = environment_name

    @cached_property
    def project(self):
        config_path = config_path_for_environment_name(
            self.ctx.playbook_path, self.environment_name)

        return get_project(
            project_dir=self.ctx.playbook_dir_path.strpath,
            config_path=config_path,
            project_name=self.ctx.compose_project_name(self.environment_name))

    def setup(self):
        if self.environment_name is None:
            return

        try:
            # ensure image builds are up-to-date
            # do not pull as image might only be available locally
            self.project.build(pull=False)
        except BuildError as err:
            fail("building service '{0}' failed with reason '{1}'".format(
                err.service.name, err.reason))

        self.project.up()

        inventory_lines = []
        for service in self.project.services:
            container_name = service.get_container().name
            inventory_line = ' '.join((
                service.name,
                'ansible_connection="goodplaydocker"',
                'ansible_become_method="dockerexec"',
                'ansible_host="{}"'.format(container_name),
            ))
            inventory_lines.append(inventory_line)
        inventory_content = '\n'.join(inventory_lines)

        # choose name 'inventory_goodplay' as it comes after 'inventory' when compared,
        # alphanumerical, otherwise Ansible does not merge in the ansible_connection
        # information correctly and thus tries to use an SSH connection
        self.ctx.extended_inventory_path.join('inventory_goodplay').write(inventory_content)

    def teardown(self):
        if self.environment_name is None:
            return

        self.project.kill()
        self.project.down(remove_image_type=False, include_volumes=True)
