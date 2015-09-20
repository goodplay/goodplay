# -*- coding: utf-8 -*-

from cached_property import cached_property


class RoleSupport(object):
    @cached_property
    def role_path(self):
        for ancestor_path in self.playbook_path.parts(reverse=True)[1:]:
            if ancestor_path.basename == 'tests':
                role_path = ancestor_path.dirpath()
                is_role_path = \
                    role_path.join('meta', 'main.yml').check(file=True)

                if is_role_path:
                    return role_path
                break
