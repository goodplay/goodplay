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

        self.extended_inventory_path = self.create_extended_inventory_path()

        self.running_containers = []

    @cached_property
    def client(self):
        return docker.Client(
            version='auto',
            **docker.utils.kwargs_from_env(assert_hostname=False))

    def create_extended_inventory_path(self):
        extended_inventory_path = py.path.local.mkdtemp()

        extended_inventory_path.join(
            self.inventory_path.basename).mksymlinkto(self.inventory_path)

        if self.inventory_path.check(dir=True):
            group_vars_path = self.inventory_path.join('group_vars')

            if group_vars_path.check(dir=True):
                extended_inventory_path.join('group_vars') \
                    .mksymlinkto(group_vars_path)

            host_vars_path = self.inventory_path.join('host_vars')

            if host_vars_path.check(dir=True):
                extended_inventory_path.join('host_vars') \
                    .mksymlinkto(host_vars_path)

        return extended_inventory_path

    def setup(self):
        self.pull_required_images()

        inventory_lines = []

        for host, container in self.start_containers():
            additional_config = self.additional_config_for_host(host, container)
            inventory_line = host.vars()['inventory_hostname'] + ' ' + \
                ' '.join(('{0}="{1}"'.format(key, value)
                          for key, value in additional_config.items()))
            inventory_lines.append(inventory_line)

        inventory_content = '\n'.join(inventory_lines)

        self.extended_inventory_path.join('goodplay').write(inventory_content)
        self.playbook.inventory_path = self.extended_inventory_path

    def pull_required_images(self):
        required_images = set()

        for host in self.inventory.hosts():
            required_image = host.vars().get('goodplay_image')

            if required_image:
                required_images.add(required_image)

        # TODO: define how to disable this caching and always pull latest
        for required_image in required_images:
            try:
                self.client.inspect_image(required_image)
            except docker.errors.NotFound:
                self.client.pull(required_image)

    def start_containers(self):
        for host in self.inventory.hosts():
            image = host.vars().get('goodplay_image')

            if not image:
                continue

            container = self.start_container(host)

            self.running_containers.append(container)

            yield host, container

    def start_container(self, host):
        host_vars = host.vars()

        hostname = host_vars['inventory_hostname']
        image = host_vars.get('goodplay_image')

        # host_config:
        # probably create a new network stack for the first container
        #   (network_mode='bridge')
        # and then reuse this network stack for the other containers
        #   (network_mode='container:[name|id]')
        #
        # cap_add probably needed when supporting KVM

        container = self.client.create_container(
            image=image,
            hostname=hostname,
            detach=True,
            tty=True,
            host_config=self.client.create_host_config()
        )

        self.client.start(container)

        return container

    def additional_config_for_host(self, host, container):
        return dict(
            ansible_connection='docker',
            ansible_host=container['Id'],
        )

    def release(self):
        self.extended_inventory_path.remove()

    def teardown(self):
        # kill and remove containers
        for container in self.running_containers:
            self.client.remove_container(container, force=True)
