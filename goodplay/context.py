# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

import hashlib
import uuid

from cached_property import cached_property
import py.path

from goodplay import ansible_support


class GoodplayContext(object):
    def __init__(self, playbook_path, config=None):
        self.playbook_path = playbook_path
        self.config = config

        self._temp_dir_paths = []

    def _create_temp_dir_path(self):
        temp_path = py.path.local.mkdtemp()
        self._temp_dir_paths.append(temp_path)
        return temp_path

    @cached_property
    def inventory_path(self):
        inventory_path = self.playbook_path.dirpath('inventory')

        if inventory_path.check():
            return inventory_path

    @cached_property
    def inventory(self):
        if self.inventory_path:
            return ansible_support.Inventory(self.inventory_path)

    @cached_property
    def extended_inventory_path(self):
        extended_inventory_path = self._create_temp_dir_path()

        extended_inventory_path.join('inventory').mksymlinkto(self.inventory_path)

        if self.inventory_path.check(dir=True):
            group_vars_path = self.inventory_path.join('group_vars')

            if group_vars_path.check(dir=True):
                extended_inventory_path.join('group_vars').mksymlinkto(group_vars_path)

            host_vars_path = self.inventory_path.join('host_vars')

            if host_vars_path.check(dir=True):
                extended_inventory_path.join('host_vars').mksymlinkto(host_vars_path)

        # when inventory_path is a file, group_vars and host_vars directories
        # are handled implicitly as they are beside the executed playbook

        return extended_inventory_path

    @cached_property
    def playbook_dir_path(self):
        return self.playbook_path.dirpath()

    @cached_property
    def playbook(self):
        if self.inventory_path:
            return ansible_support.Playbook(self)

    @cached_property
    def is_role_playbook(self):
        return bool(self.role_path)

    @cached_property
    def role_path(self):
        for ancestor_path in self.playbook_path.parts(reverse=True)[1:]:
            if ancestor_path.basename == 'tests':
                role_path = ancestor_path.dirpath()
                is_role_path = role_path.join('meta', 'main.yml').check(file=True)

                if is_role_path:
                    return role_path
                break

    @cached_property
    def role_under_test_roles_path(self):
        role_under_test_roles_path = self._create_temp_dir_path()

        role_under_test_roles_path.join(self.role_path.basename).mksymlinkto(self.role_path)

        return role_under_test_roles_path

    @cached_property
    def installed_roles_path(self):
        return self._create_temp_dir_path()

    @cached_property
    def use_local_roles(self):
        return self.config.getoption('use_local_roles')

    def compose_project_name(self, environment_name):
        node_id = '{:x}'.format(uuid.getnode())
        project_name_parts = ':'.join((node_id, self.playbook_path.strpath, environment_name))
        project_hash = hashlib.sha1(project_name_parts.encode('utf-8')).hexdigest()[:8]

        return 'goodplay{}'.format(project_hash)

    def release(self):
        for temp_path in reversed(self._temp_dir_paths):
            temp_path.remove(ignore_errors=True)
        self._temp_dir_paths = []
