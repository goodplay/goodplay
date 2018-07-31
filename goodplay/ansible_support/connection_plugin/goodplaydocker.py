# -*- coding: utf-8 -*-

# This connection plugin has been implemented as the docker connection plugin
# provided by Ansible does not support become_user with Docker's native user
# management (as of version 2.1.0). The necessary changes have been
# implemented in PR ansible/ansible#15556 but not accepted.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

import ansible.constants as C
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
