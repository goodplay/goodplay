.. _config:

Configuring with .goodplay.yml
==============================

Having a central configuration source around eases things when it comes
to maintaining an increasingly number of test scenarios.

For this goodplay allows you to provide a ``.goodplay.yml`` file that contains
commonly used configuration.
goodplay searches for ``.goodplay.yml`` file beside a test playbook and in the
directories above until it finds the first one.


Platforms
---------

Currently ``.goodplay.yml`` is only used for mapping platforms to Docker
images:

.. code-block:: yaml

   ## .goodplay.yml
   platforms:
     - name: EL
       version: 6
       image: centos:centos6

     - name: EL
       version: 7
       image: centos:centos7

This enables you to test your Ansible roles against multiple platforms, see
:ref:`parametrizing-platform` for details.
