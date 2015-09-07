# -*- coding: utf-8 -*-

from cached_property import cached_property

from .base import PlaybookMixin


class RoleSupport(PlaybookMixin):
    @cached_property
    def is_role_test_playbook(self):
        return bool(self.role_path)

    @cached_property
    def role_path(self):
        for ancestor_dir in self.playbook_path.parts(reverse=True)[1:]:
            if ancestor_dir.basename == 'tests':
                potential_role_path = ancestor_dir.dirpath()
                potential_meta_path = potential_role_path.join('meta', 'main.yml')

                if potential_meta_path.check(file=1):
                    return potential_role_path
                break
