# -*- coding: utf-8 -*-

from cached_property import cached_property


class RoleSupport(object):
    @cached_property
    def role_path(self):
        for ancestor_dir in self.playbook_path.parts(reverse=True)[1:]:
            if ancestor_dir.basename == 'tests':
                potential_role_path = ancestor_dir.dirpath()
                potential_meta_path = potential_role_path.join('meta', 'main.yml')

                if potential_meta_path.check(file=1):
                    return potential_role_path
                break
