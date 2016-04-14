Command-Line Options
====================

Additionally to the default ``py.test`` command-line options, goodplay
provides the following options for ``goodplay`` and ``py.test`` executables.


``--use-local-roles``
---------------------

By default goodplay creates a temporary directory for installing dependent
roles and ensures that has highest precedence when resolving Ansible roles.
This is done to ensure your test run doesn't interfere with other roles in
your `Ansible roles path`_.

There might be cases where you want to disable this default behavior, and
give the configured `Ansible roles path`_ highest precedence, e.g.:

#. When you're developing multiple Ansible roles at once and you want to
   test-run them together.

#. When you cannot use Ansible Galaxy's dependency resolution due to Ansible
   roles being stored in a non-supported location, e.g. non-supported
   version control system.

When running with ``--use-local-roles`` switch, please ensure you have either
``ANSIBLE_ROLES_PATH`` environment variable set, or ``roles_path`` configured
in your ``ansible.cfg``.

.. _`Ansible roles path`: http://docs.ansible.com/ansible/intro_configuration.html#roles-path
