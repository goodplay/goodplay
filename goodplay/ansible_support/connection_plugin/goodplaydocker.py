# -*- coding: utf-8 -*-

# This connection plugin has been implemented as the docker connection plugin
# provided by Ansible does not support become_user with Docker's native user
# management (as of version 2.1.0). The necessary changes have been
# implemented in PR ansible/ansible#15556 but not accepted.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

import re

from ansible import __version__ as ansible_version
import ansible.constants as C
from ansible.errors import AnsibleError
from ansible.playbook.play_context import PlayContext
import ansible.plugins.connection.docker


def monkeypatch_play_context():
    original_make_become_cmd = PlayContext.make_become_cmd

    def make_become_cmd_with_dockerexec(self, cmd, executable=None):
        if self.become and self.become_method == 'dockerexec':
            self.prompt = None
            return cmd

        return original_make_become_cmd(self, cmd, executable)

    PlayContext.make_become_cmd = make_become_cmd_with_dockerexec


monkeypatch_play_context()


class Connection(ansible.plugins.connection.docker.Connection):
    transport = 'goodplaydocker'

    become_methods = set(C.BECOME_METHODS).difference({'su'}).union({'dockerexec'})

    def _build_exec_cmd(self, cmd):
        local_cmd = [self.docker_cmd]

        if self._play_context.docker_extra_args:
            local_cmd += self._play_context.docker_extra_args.split(' ')

        local_cmd += ['exec']

        if self._play_context.become and self._play_context.become_method == 'dockerexec':
            exec_user = self._play_context.become_user
        else:
            exec_user = self.remote_user

        if exec_user is not None:
            local_cmd += ['-u', exec_user]

        # -i is needed to keep stdin open which allows pipelining to work
        local_cmd += ['-i', self._play_context.remote_addr] + cmd

        return local_cmd


# Ansible 2.2 specific fixes
if ansible_version.startswith('2.2.'):
    @staticmethod
    def _sanitize_version(version):
        return re.sub(b'[^0-9a-zA-Z\.]', b'', version)

    def _get_docker_version(self):
        cmd, cmd_output, err, returncode = self._old_docker_version()
        if returncode == 0:
            for line in cmd_output.split(b'\n'):
                if line.startswith(b'Server version:'):  # old docker versions
                    return self._sanitize_version(line.split()[2]).decode('utf-8')

        cmd, cmd_output, err, returncode = self._new_docker_version()
        if returncode:
            raise AnsibleError('Docker version check (%s) failed: %s' % (cmd, err))

        return self._sanitize_version(cmd_output).decode('utf-8')

    Connection._sanitize_version = _sanitize_version
    Connection._get_docker_version = _get_docker_version
