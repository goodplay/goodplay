# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

from ansible import __version__ as ansible_version

try:
    from ansible.inventory.manager import InventoryManager
except ImportError:
    import ansible.inventory

from ansible.parsing.dataloader import DataLoader
from ansible.utils.vars import load_extra_vars

try:
    from ansible.vars.manager import VariableManager
except ImportError:
    from ansible.vars import VariableManager
    import ansible.vars


class EmptyOptions(object):
    extra_vars = []


class Inventory(object):
    def __init__(self, inventory_path):
        self.inventory_path = inventory_path
        self.inventory = None
        self.inventory = self.build_inventory()

    def build_inventory(self):
        self.clear_caches()

        loader = DataLoader()

        # Ansible 2.2 and 2.3 specific fixes
        if ansible_version.startswith('2.2.') or ansible_version.startswith('2.3.'):
            variable_manager = ansible.vars.VariableManager()
            variable_manager.extra_vars = load_extra_vars(
                loader=loader, options=EmptyOptions())

            inventory = ansible.inventory.Inventory(
                loader=loader,
                variable_manager=variable_manager,
                host_list=self.inventory_path.strpath)
            variable_manager.set_inventory(inventory)
        # Ansible 2.4+
        else:
            inventory = InventoryManager(loader=loader, sources=self.inventory_path.strpath)
            variable_manager = VariableManager(
                loader=loader, inventory=inventory)
            variable_manager.extra_vars = load_extra_vars(
                loader=loader, options=EmptyOptions())

        return inventory

    def clear_caches(self):
        # Ansible 2.2 and 2.3 specific fixes
        if ansible_version.startswith('2.2.') or ansible_version.startswith('2.3.'):
            # unfortunately we have to reset caches as these are kept as module state
            ansible.inventory.HOSTS_PATTERNS_CACHE.clear()
            ansible.vars.HOSTVARS_CACHE.clear()
        # Ansible 2.4+
        elif self.inventory is not None:
            self.inventory.clear_caches()

    def hosts(self):
        self.clear_caches()

        return [Host(host) for host in self.inventory.get_hosts()]


class Host(object):
    def __init__(self, host):
        self.host = host

    def vars(self):
        return self.host.get_vars()
