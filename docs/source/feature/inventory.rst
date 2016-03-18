.. _inventory:

Defining Environment
====================

Prior to writing tests it is important to define the environment the tests
are going to ran on, e.g. hostnames and platforms.
Throughout this documentation we will often refer to this as *inventory*.

goodplay borrows this term from Ansible which already provides
`various ways to define inventories`_.
When doing a test run, goodplay reads an inventory during setup phase that
defines the hosts to be used for the test.
These can be hosts you have already available in your environment or Docker
containers that are automatically created as we will see in a minute.

The usual and easiest way to define an *inventory* is to create a file
named ``inventory`` right beside the :ref:`test playbook <writing-test-playbook>`:

.. code-block:: yaml

   ## inventory
   web ansible_user=root
   db ansible_user=root

This example defines two hosts -- ``web`` and ``db``.
The remote user that is used to connect to the host needs to be specified
via ``ansible_user`` inventory variable.

.. _`various ways to define inventories`: https://docs.ansible.com/ansible/intro_inventory.html


Specifying Platform
-------------------

If we would use the inventory example from the previous section together with
a test playbook it would not create any Docker containers yet.
There are multiple reasons this is not done automatically:

#. goodplay can be used without Docker, i.e. tests run on localhost.
#. Some hostnames defined in the inventory may be used only for configuration
   purposes (not actually required for test run).
#. Hosts may require different platforms, so these must be specified
   explicitly.

The platform for a host can be specified via the host variable
``goodplay_image``.

Let's assume we want host ``web`` to run latest CentOS 6 and host ``db`` to
run latest CentOS 7, we could update the inventory file:

.. code-block:: yaml

   ## inventory
   web goodplay_image=centos:centos6 ansible_user=root
   db goodplay_image=centos:centos7 ansible_user=root


.. _`parametrizing-platform`:

Parametrizing Platform
----------------------

.. note::

   This is only supported when testing Ansible roles.
   This may probably be supported for all goodplay tests in a later version.

In case you want to test an Ansible role against multiple platforms, you can
specify ``goodplay_platform=*`` on hosts in inventory.

goodplay will then matrix test your Ansible role against all supported
platforms that are mentioned in the role's ``meta/main.yml`` file, provided
that the platforms have been mapped to Docker images in
:ref:`.goodplay.yml config file <config>`.
