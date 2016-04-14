.. _`test-playbook`:

Writing Tests
=============

goodplay builds upon *playbooks* -- Ansible_'s configuration, deployment, and
orchestration language.

.. _Ansible: https://docs.ansible.com/


Ansible Terminology
-------------------

Quoting from Ansible's documentation:

.. epigraph::

   At a basic level, playbooks can be used to manage configurations of and
   deployments to remote machines. At a more advanced level, they can
   sequence multi-tier rollouts involving rolling updates, and can delegate
   actions to other hosts, interacting with monitoring servers and load
   balancers along the way.

A pseudo *playbook* -- written as a YAML_ file -- may look like this:

.. code-block:: yaml

   ## playbook_name.yml
   # play #1
   - hosts: host1:host2
     tasks:
       # play #1, task #1
       - name: first task name
         module1:
           arg1: value1
           arg2: value2

       # play #1, task #2
       - name: second task name
         module2:
           arg1: value1
           arg2: value2
         tags: specialtag

   # play #2
   - hosts: host3
     tasks:
       # play #2, task #1
       - name: another task name
         module1:
           arg1: value1

Each *playbook* is composed of one or more *plays*.

Each *play* basically defines two things:

- on which *hosts* to run a particular set of *tasks*, and
- what *tasks* to run on each of these *hosts*.

A *task* refers to the invocation of a *module* which can be
e.g. something like creating a user, installing a package,
or starting a service.
Ansible already comes bundled with a large `module library`_.

.. _YAML: https://en.wikipedia.org/wiki/YAML
.. _`module library`: https://docs.ansible.com/ansible/modules.html


.. _`writing-test-playbook`:

Writing Test Playbooks
----------------------

After we have briefly introduced the basic terminology of the Ansible
language, it is now time to define what a *test playbook* looks like in the
goodplay context.

A *test playbook* is as the name implies a *playbook* with the following
contraints:

#. The filename is prefixed with ``test_``.
#. The filename extension is ``.yml``.
#. Right beside the *test playbook* a file or directory named ``inventory``
   exists. See :ref:`environment` for details.
#. If you want to test against Docker containers you may optionally put a
   ``docker-compose.yml`` file right beside the *test playbook*.
#. The *test playbook* contains or includes at least one task tagged with
   ``test``, also called *test task*.
#. Within a *test playbook* all *test task* names must be unique.


Basic Example
~~~~~~~~~~~~~

An example test playbook that verifies that two hosts (``host1`` and ``host2``
created as Docker containers, each one running ``centos:centos6`` platform
image) are reachable:

.. code-block:: yaml

   ## docker-compose.yml
   version: "2"
   services:
     host1:
       image: "centos:centos6"
       tty: True

     host2:
       image: "centos:centos6"
       tty: True

   ## inventory
   host1 ansible_user=root
   host2 ansible_user=root

.. code-block:: yaml

   ## test_ping_hosts.yml
   - hosts: host1:host2
     tasks:
       - name: hosts are reachable
         ping:
         tags: test

The name of the single test task is ``hosts are reachable``.
The test task only passes when the task runs successful on both hosts
i.e. both hosts are reachable.


Complex Example
~~~~~~~~~~~~~~~

A slightly more complicated example making use of more advanced Ansible
features, like defining host groups or registering variables and using
Ansible's assert module:

.. code-block:: yaml

   ## install_myapp.yml
   - hosts: myapp-hosts
     tasks:
       - name: install myapp
         debug:
           msg: "Do whatever is necessary to install the app"

.. code-block:: yaml

   ## tests/docker-compose.yml
   version: "2"
   services:
     host1:
       image: "centos:centos6"
       tty: True

     host2:
       image: "centos:centos6"
       tty: True

   ## tests/inventory
   [myapp-hosts]
   host1 ansible_user=root
   host2 ansible_user=root

.. code-block:: yaml

   ## tests/test_myapp.yml
   - include: ../install_myapp.yml

   - hosts: myapp-hosts
     tasks:
       - name: config file is only readable by owner
         file:
           path: /etc/myapp/myapp.conf
           mode: 0400
           state: file
         tags: test

       - name: fetch content of myapp.log
         command: cat /var/log/myapp.log
         register: myapp_log
         changed_when: False

       - name: myapp.log contains no errors
         assert:
           that: "'ERROR' not in myapp_log.stdout"
         tags: test


Writing Tests for Ansible Roles
-------------------------------

To keep playbooks organized in a consistent manner and make them reusable,
Ansible provides the concept of `Ansible Roles`_.
An Ansible role is defined as a directory (named after the role) with
subdirectories named by convention:

.. code-block:: none

   role/
     defaults/
     files/
     handlers/
     meta/
     tasks/
     templates/
     vars/

When writing tests for your role, goodplay expects another subdirectory
by convention:

.. code-block:: none

   role/
     ...
     tests/

By following this convention, goodplay takes care of making the Ansible
role available on the `Ansible Roles Path`_, so you can use them directly in
your test playbook.

.. _`Ansible Roles`: https://docs.ansible.com/ansible/playbooks_roles.html#roles
.. _`Ansible Roles Path`: http://docs.ansible.com/ansible/intro_configuration.html#roles-path
