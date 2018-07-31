# -*- coding: utf-8 -*-

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.utils.vars import load_extra_vars

from ansible.vars.manager import VariableManager


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
        inventory = InventoryManager(
            loader=loader, sources=self.inventory_path.strpath)
        variable_manager = VariableManager(
            loader=loader, inventory=inventory)
        variable_manager.extra_vars = load_extra_vars(
            loader=loader, options=EmptyOptions())

        return inventory

    def clear_caches(self):
        if self.inventory is not None:
            self.inventory.clear_caches()

    def hosts(self):
        self.clear_caches()

        return [Host(host) for host in self.inventory.get_hosts()]


class Host(object):
    def __init__(self, host):
        self.host = host

    def vars(self):
        return self.host.get_vars()
