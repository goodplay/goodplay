.. _quickstart:

Quickstart
==========

Eager to get started? This page gives a good introduction in how to get started
with goodplay.

For our basic example we assume we want to test our existing playbook
that is responsible for installing and configuring a plain nginx.

Our playbook might look something like this:

.. code-block:: yaml

   # nginx_install.yml
   ---
   - hosts: default
     become: yes

     tasks:
       - name: install nginx package
         apt:
           name: nginx
           state: latest
           update_cache: yes


At a first glance this looks fine but it is not clear, if:

1. The nginx service has been automatically started after the installation.

2. The nginx service is started at boot-time.

3. The nginx is running on port 80.


So, let's write some tests that ensure nginx is installed correctly:


.. code-block:: yaml

   # test_nginx_install.yml
   ---
   - include: nginx_install.yml

   - hosts: default
     become: yes

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

You may have noticed that all we have to do is use the same ansible modules
we're already used to. All that needs to be added is the ``test`` tag.
