# -*- coding: utf-8 -*-

from cached_property import cached_property

import docker
import docker.errors
import docker.utils

import py.path


class DockerRunner(object):
    def __init__(self, inventory_path, inventory, playbook):
        self.inventory_path = inventory_path
        self.inventory = inventory
        self.playbook = playbook

        self.extended_inventory_path = py.path.local.mkdtemp()
        self.extended_inventory_path.join(
            self.inventory_path.basename).mksymlinkto(self.inventory_path)

        if self.inventory_path.check(dir=True):
            group_vars_path = self.inventory_path.join('group_vars')

            if group_vars_path.check(dir=True):
                self.extended_inventory_path.join('group_vars') \
                    .mksymlinkto(group_vars_path)

            host_vars_path = self.inventory_path.join('host_vars')

            if host_vars_path.check(dir=True):
                self.extended_inventory_path.join('host_vars') \
                    .mksymlinkto(host_vars_path)

        self.containers = []

    @cached_property
    def client(self):
        return docker.Client(
            **docker.utils.kwargs_from_env(assert_hostname=False))

    def up(self):
        # host_config:
        # probably create a new network stack for the first container
        #   (network_mode='bridge')
        # and then reuse this network stack for the other containers
        #   (network_mode='container:[name|id]')
        #
        # cap_add probably needed when supporting KVM

        # check required images
        required_images = set()

        for host in self.inventory.hosts():
            required_image = host.vars().get('goodplay_image')

            if required_image:
                required_images.add(required_image)

        # pull required images
        # TODO: define how to disable this caching and always pull latest
        for required_image in required_images:
            try:
                self.client.inspect_image(required_image)
            except docker.errors.NotFound:
                self.client.pull(required_image)

        # start containers
        inventory_lines = []

        for host in self.inventory.hosts():
            host_vars = host.vars()

            hostname = host_vars['inventory_hostname']
            image = host_vars.get('goodplay_image')

            if not image:
                continue

            container = self.client.create_container(
                image=image,
                hostname=hostname,
                detach=True,
                tty=True,
                host_config=self.client.create_host_config()
            )
            self.client.start(container)
            self.containers.append(container)

            inventory_line = \
                '{0} ansible_connection=docker ansible_host={1}'.format(
                    hostname, container['Id'])
            inventory_lines.append(inventory_line)

            print 'container started: {0!r}'.format(container)

        inventory_content = '\n'.join(inventory_lines)

        self.extended_inventory_path.join('goodplay').write(inventory_content)
        self.playbook.inventory_path = self.extended_inventory_path

    def release(self):
        self.extended_inventory_path.remove()

    def destroy(self):
        # stop containers
        for container in self.containers:
            self.client.remove_container(container, force=True)

            print 'container stopped: {0!r}'.format(container)
