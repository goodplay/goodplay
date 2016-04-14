.. _environment:

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
containers you have defined via Docker Compose that are automatically created,
as we will see in a minute.

The usual and easiest way to define an *inventory* is to create a file
named ``inventory`` right beside the
:ref:`test playbook <writing-test-playbook>`:

.. code-block:: yaml

   ## inventory
   web ansible_user=root
   db ansible_user=root

This example defines two hosts -- ``web`` and ``db``.
The remote user that is used to connect to the host needs to be specified
via ``ansible_user`` inventory variable.

.. _`various ways to define inventories`: https://docs.ansible.com/ansible/intro_inventory.html


Single Docker Environment
-------------------------

If we would use the inventory example from the previous section together with
a test playbook it would not create any Docker containers yet, and thus Ansible
would not be able to connect to the hosts ``web`` and ``db``.
There are multiple reasons this is not done automatically:

#. goodplay can be used without Docker, e.g. tests can run against localhost
   or otherwise managed test environment.
#. Some hostnames defined in the inventory may be used only for configuration
   purposes (not actually required for test run).
#. Hosts may require different platforms, so these must be specified
   explicitly.

The Docker container environment required for a test run is specified with
the help of `Docker Compose`_ in a ``docker-compose.yml`` file right beside the
test playbook and inventory.

.. note::

   Please note that Docker Compose uses the term *service* for what goodplay
   uses the term *host*.

Let's assume we want hosts ``web`` and ``db`` to run latest CentOS 7.
Therefor we create the following ``docker-compose.yml`` file:

.. code-block:: yaml

   ## docker-compose.yml
   version: "2"
   services:
     web:
       image: "centos:centos7"
       tty: True

     db:
       image: "centos:centos7"
       tty: True

When executing a test, goodplay ...

* ... recognizes the ``docker-compose.yml`` file right beside the test playbook
  and inventory,
* ... starts up the test environment,
* ... connects the Ansible inventory with the instantiated Docker containers,
* ... executes the test playbook,
* ... and finally shuts down the test environment.

.. _`Docker Compose`: https://docs.docker.com/compose/


Multiple Docker Environments
----------------------------

Sometimes you want to run the same test playbook against multiple environments.
For example when you have an Ansible role that should support more than one
platform, you most likely want to test run it against each supported platform.

We could extend our previous example by not only testing against latest
CentOS 7, but also against Ubuntu Trusty:

.. code-block:: yaml

   ## docker-compose.centos.7.yml
   version: "2"
   services:
     web:
       image: "centos:centos7"
       tty: True

     db:
       image: "centos:centos7"
       tty: True


   ## docker-compose.ubuntu.trusty.yml
   version: "2"
   services:
     web:
       image: "ubuntu-upstart:trusty"
       tty: True

     db:
       image: "ubuntu-upstart:trusty"
       tty: True

goodplay will recognize that there are multiple Docker Compose files, and will
run the test playbook against each of these environments.

Docker Compose allows you to work with `Multiple Docker Compose files`_.
goodplay takes this one step further by introducing conventions to
extending/overriding Docker Compose files.

goodplay sees your ``docker-compose.yml`` files as a hierarchy where as
``docker-compose.yml`` is the parent of ``docker-compose.item1.yml`` which
is the parent of ``docker-compose.item1.item11.yml`` and so on and so forth.
When deciding which ones to use, goodplay only instantiates the leaves in
the hierarchy. Thus you could have intermediate Docker Compose files that
hold common configuration that can be refered to further down in the
hierarchy.

Additionally one can use the extension ``.override.yml`` instead of ``.yml``
to make goodplay override (merge) the Docker Compose file from the same or
upper level.

.. _`Multiple Docker Compose files`: https://docs.docker.com/compose/extends/
