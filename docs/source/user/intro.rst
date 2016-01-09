.. _introduction:

Introduction
============

Writing good tests for your existing deployments or distributed software
infrastructure should be painless, and easily accomplishable without
involving any time-consuming and complex testing setup.
This is where goodplay comes into play.

goodplay instruments Ansible_ --- "a radically simple IT automation platform"
as it is advertized --- and allows you to write your tests in the same simple
and probably already familiar language you would write an `Ansible playbook`_.

.. _Ansible: https://docs.ansible.com/
.. _`Ansible playbook`: https://docs.ansible.com/playbooks.html


Features
--------

* define your test environments as `Ansible inventories`_
* write your tests as `Ansible 2.x playbook tasks`_
* resolve and auto-install Ansible role dependencies prior to test run
* run your tests within Docker_ container(s) or on localhost
* built as a pytest_ plugin, so you can run your goodplay tests together with your other tests

.. _`Ansible 2.x playbook tasks`: https://docs.ansible.com/playbooks.html
.. _`Ansible inventories`: https://docs.ansible.com/ansible/intro_inventory.html
.. _Docker: https://www.docker.com/
.. _pytest: https://pytest.org/


Versioning
----------

goodplay will use `Semantic Versioning`_ when reaching v1.0.0.
Until then, the minor version is used for backwards-incompatible changes.

.. _`Semantic Versioning`: http://semver.org/


License
-------

goodplay is open source software released under the Apache License 2.0:

.. include:: ../../../LICENSE
