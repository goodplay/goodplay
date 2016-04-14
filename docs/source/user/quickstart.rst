.. _`getting-started`:

Quick Start
===========

Eager to get started? This page gives a good introduction in how to get
started with goodplay.

For our basic example we assume we want to test our existing Ansible playbook
that is responsible for installing a plain nginx web server on Ubuntu_:

.. code-block:: yaml

   ## nginx_install.yml
   - hosts: web
     tasks:
       - name: install nginx package
         apt:
           name: nginx
           state: latest
           update_cache: yes

Briefly summarized, when running the playbook via ``ansible-playbook``,
Ansible will:

#. Connect to host ``web``.
#. Update the cache of ``apt``, which is Ubuntu's default package manager.
#. Install the latest ``nginx`` -- one of the most used web servers -- package
   via ``apt``.

At a first glance this looks fine but it is not clear if the following holds true:

#. The nginx service is automatically started after the installation.
#. The nginx service is started at boot time.
#. The nginx service is running on port 80.

Let's turn these assumptions into requirements which we are going to test
with goodplay.
But, first things first... we need to install goodplay.

.. _Ubuntu: http://www.ubuntu.com/


Installing
----------

Before installing goodplay make sure you have Docker installed, which is a
prerequisite for this quick start tutorial.
Check out the official `Install Docker Engine`_ guide.

Afterwards, to install goodplay with pip_, just run this in your terminal::

   $ pip install goodplay

Please consult the :ref:`Installation Guide <installation>` for detailed information
and alternative installation options.

.. _`Install Docker Engine`: https://docs.docker.com/engine/installation/
.. _pip: https://pip.pypa.io


Defining Environment
--------------------

Before writing the actual tests we need to define our test environment
which is created as Docker containers behind the scenes.
This is done via a `Docker Compose file`_ and an `Ansible inventory`_ where
we define all hosts and groups required for the test run.

In our case we want to test our nginx installation on a single host with
Ubuntu Trusty:

.. code-block:: yaml

   ## tests/docker-compose.yml
   version: "2"
   services:
     web:
       image: "ubuntu-upstart:trusty"
       tty: True

   ## tests/inventory
   web ansible_user=root

In this example we define a *host* (in Docker Compose terminology this is a
*service*) with name ``web`` that runs the `official Docker Ubuntu image`_
``ubuntu-upstart:trusty``.

- :ref:`Feature: Defining Environment <environment>`

.. _`Ansible inventory`: https://docs.ansible.com/ansible/intro_inventory.html
.. _`Docker Compose file`: https://docs.docker.com/compose/compose-file/
.. _`official Docker Ubuntu image`: https://hub.docker.com/_/ubuntu-upstart/


Writing Tests
-------------

Now, let's write some tests that ensure nginx is installed according to our
requirements:

.. code-block:: yaml

   ## tests/test_nginx_install.yml
   - include: ../nginx_install.yml

   - hosts: web
     tasks:
       - name: nginx service is running
         service:
           name: nginx
           state: started
         tags: test

       - name: nginx service is enabled
         service:
           name: nginx
           enabled: yes
         tags: test

       - name: nginx service is listening on port 80
         wait_for:
           port: 80
           timeout: 10
         tags: test

You may have noticed that all we have to do is use the same Ansible modules
we're already used to.
In case you are new to all this playbook stuff, the official
`Ansible playbook guide`_ will help you getting started.

Labeling a playbook's task with a ``test`` tag makes goodplay recognize it
as a *test task*. A *test task* is meant to be successful (passes) when it
does not result in a change and does not fail.

- :ref:`Feature: Writing Tests <test-playbook>`

.. _`Ansible playbook guide`: https://docs.ansible.com/ansible/playbooks.html


Running Tests
-------------

.. note::

   First-time run may take some more seconds or minutes (depending on your
   internet connection) as the required Docker images need to be downloaded.

The following command will kick-off the test run::

   $ goodplay -v
   ============================= test session starts ==============================
   platform darwin -- Python 2.7.6, pytest-2.9.1, py-1.4.31, pluggy-0.3.1 -- /Users
   /benjixx/.virtualenvs/goodplay/bin/python2.7
   rootdir: /Users/benjixx/src/goodplay/examples/quickstart
   plugins: goodplay-0.6.0
   collected 3 items

   tests/test_nginx_install.yml::nginx service is running PASSED
   tests/test_nginx_install.yml::nginx service is enabled PASSED
   tests/test_nginx_install.yml::nginx service is listening on port 80 PASSED

   ========================== 3 passed in 43.13 seconds ===========================
