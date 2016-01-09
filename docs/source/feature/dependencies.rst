Auto-Installing Dependencies
============================

Ansible comes bundled with ``ansible-galaxy``, a tool to install Ansible roles
either from central `Ansible Galaxy`_, or e.g. from a version control system.

goodplay uses ``ansible-galaxy`` under the hood to auto-install dependencies
required by your test playbooks. Dependencies are distiguished into two
categories -- *hard dependencies* and *soft dependencies*.

.. warning::

   Installing Ansible roles that are maintained by a third-party from
   Ansible Galaxy may come with its own security risks.
   So please ensure you know what you're doing and/or install your own roles
   from your own version control system.

.. _`Ansible Galaxy`: https://galaxy.ansible.com/


Hard Dependencies
-----------------

When writing tests for an Ansible role (i.e. under a role's ``tests``
directory), goodplay ensures all dependent Ansible roles defined in the role's
``meta/main.yml`` file are automatically installed and made available in the
test context.

We refer to this as *hard dependencies* as these are expected to be required
for successfully using an Ansible role.


Soft Dependencies
-----------------

*Soft dependencies* refer to dependent Ansible roles that are only required
for test execution, e.g. setting up a third party software component we
support to integrate with.

Soft dependencies need to be specified as ``requirements.yml`` files right
beside the test playbook that depends on them, and must follow the guidelines
outlined in the `Ansible Galaxy Requirements File`_ documentation.

.. _`Ansible Galaxy Requirements File`: https://docs.ansible.com/ansible/galaxy.html#advanced-control-over-role-requirements-files
