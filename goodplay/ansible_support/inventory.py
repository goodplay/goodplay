# -*- coding: utf-8 -*-

import ansible
import ansible.inventory
import ansible.parsing.dataloader
import ansible.utils.vars
import ansible.vars


class EmptyOptions(object):
    extra_vars = []


class Inventory(object):
    def __init__(self, inventory_path):
        self.inventory_path = inventory_path
        self.inventory = self.build_inventory()

    def build_inventory(self):
        self.clear_host_caches()

        loader = ansible.parsing.dataloader.DataLoader()
        variable_manager = ansible.vars.VariableManager()
        variable_manager.extra_vars = ansible.utils.vars.load_extra_vars(
            loader=loader, options=EmptyOptions())

        inventory = ansible.inventory.Inventory(
            loader=loader,
            variable_manager=variable_manager,
            host_list=str(self.inventory_path))
        variable_manager.set_inventory(inventory)

        return inventory

    def clear_host_caches(self):
        # unfortunately we have to reset caches as these are kept as module state
        ansible.inventory.HOSTS_PATTERNS_CACHE.clear()
        ansible.vars.HOSTVARS_CACHE.clear()

    def hosts(self):
        self.clear_host_caches()

        return [Host(host) for host in self.inventory.get_hosts()]


class Host(object):
    def __init__(self, host):
        self.host = host

    def vars(self):
        return self.host.get_vars()
