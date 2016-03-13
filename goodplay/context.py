# -*- coding: utf-8 -*-

from cached_property import cached_property
import py.path
import yaml

from goodplay import ansible_support
from goodplay.config import get_goodplay_config


class GoodplayContext(object):
    def __init__(self, playbook_path, pytestconfig=None):
        self.playbook_path = playbook_path
        self.pytestconfig = pytestconfig

        self._temp_paths = []

    def _create_temporary_dir(self):
        temp_path = py.path.local.mkdtemp()
        self._temp_paths.append(temp_path)
        return temp_path

    @cached_property
    def config(self):
        return get_goodplay_config(self.playbook_path)

    @cached_property
    def platform_manager(self):
        platform_manager = PlatformManager.from_dicts(self.config['platforms'])

        if self.is_platform_matrix_requested:
            platforms = self.role_meta_info['galaxy_info'].get('platforms', [])
            for platform in platforms:
                name = platform['name']

                for version in platform['versions']:
                    platform_manager.select_platform_by_name_and_version(name, version)

        return platform_manager

    @cached_property
    def is_platform_matrix_requested(self):
        is_goodplay_platform_wildcard_used = \
            any(host.vars().get('goodplay_platform', None) == '*'
                for host in self.inventory.hosts())

        return self.is_role_playbook and is_goodplay_platform_wildcard_used

    @cached_property
    def platforms(self):
        return self.platform_manager.selected_platforms

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
        extended_inventory_path = self._create_temporary_dir()

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
    def role_meta_info(self):
        return yaml.safe_load(self.role_path.join('meta', 'main.yml').read())

    @cached_property
    def role_under_test_roles_path(self):
        role_under_test_roles_path = self._create_temporary_dir()

        role_under_test_roles_path.join(self.role_path.basename).mksymlinkto(self.role_path)

        return role_under_test_roles_path

    @cached_property
    def installed_roles_path(self):
        return self._create_temporary_dir()

    @cached_property
    def use_local_roles(self):
        return self.pytestconfig.getoption('use_local_roles')

    def release(self):
        for temp_path in reversed(self._temp_paths):
            temp_path.remove(ignore_errors=True)


class PlatformManager(object):
    def __init__(self, available_platforms):
        self.available_platforms = available_platforms

        self.selected_platforms = []

    @classmethod
    def from_dicts(cls, platform_dicts):
        available_platforms = [Platform(**platform_dict) for platform_dict in platform_dicts]
        return PlatformManager(available_platforms)

    def find_by_id(self, id):
        if ':' not in id:
            return None

        name, version = id.split(':', 1)

        return self.find_by_name_and_version(name, version)

    def find_by_name_and_version(self, name, version):
        platform_template = Platform(name, version)

        try:
            index = self.available_platforms.index(platform_template)
            return self.available_platforms[index]
        except ValueError:
            pass

    def select_platform_by_name_and_version(self, name, version):
        platform = self.find_by_name_and_version(name, version)

        if platform and platform not in self.selected_platforms:
            self.selected_platforms.append(platform)


class Platform(object):
    def __init__(self, name, version, image=None, **kwargs):
        self.name = name
        self.version = version
        self.image = image

    def __str__(self):
        return '{0!s}:{1!s}'.format(self.name, self.version)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and str(self) == str(other))

    def __ne__(self, other):
        return not self.__eq__(other)
