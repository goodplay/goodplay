# -*- coding: utf-8 -*-

from __future__ import absolute_import

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

    def hosts(self):
        return [Host(host) for host in self.inventory.get_hosts()]


class Host(object):
    def __init__(self, host):
        self.host = host

    def vars(self):
        return self.host.get_vars()
