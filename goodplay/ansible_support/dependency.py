# -*- coding: utf-8 -*-

import os

import py.path
import yaml

from ..utils.subprocess import run


class DependencySupport(object):
    def initialize(self):
        self.installed_roles_path = py.path.local.mkdtemp()
        self.install_all_dependencies()

    def release(self):
        self.installed_roles_path.remove()

    def env(self):
        roles_path = []
        if self.role_path:
            role_base_path = self.role_path.dirpath()
            roles_path.append(str(role_base_path))
        roles_path.append(str(self.installed_roles_path))

        return dict(ANSIBLE_ROLES_PATH=os.pathsep.join(roles_path))

    def install_all_dependencies(self):
        self.install_role_dependencies()
        self.install_soft_dependencies()

    def install_role_dependencies(self):
        if not self.role_path:
            return

        role_meta_path = self.role_path.join('meta', 'main.yml')
        role_meta_content = yaml.safe_load(role_meta_path.read())
        role_dependencies = role_meta_content.get('dependencies', [])

        if role_dependencies:
            requirements_file = \
                self.installed_roles_path.join('requirements.yml')
            requirements_file.write(yaml.dump(role_dependencies))

            self.install_roles_from_requirements_file(requirements_file)

    def install_soft_dependencies(self):
        requirements_file = self.playbook_path.dirpath('requirements.yml')

        if requirements_file.check(file=True):
            self.install_roles_from_requirements_file(requirements_file)

    def install_roles_from_requirements_file(self, requirements_file):
        process = run(
            'ansible-galaxy install -vvvv --force '
            '--role-file {0} --roles-path {1}',
            requirements_file, self.installed_roles_path)

        print ''.join(process.stdout.readlines())
        if process.returncode != 0:
            raise Exception(process.stderr.readlines())
