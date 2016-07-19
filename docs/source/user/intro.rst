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

* define your test environments via `Docker Compose`_ and
  `Ansible inventories`_
* write your tests as `Ansible 2.x playbook tasks`_
* resolve and auto-install Ansible role dependencies prior to test run
* run your tests within Docker_ container(s), an already existing test
  environment, or on localhost
* built as a pytest_ plugin to have a solid test runner foundation,
  plus you can run your goodplay tests together with your other tests

.. _`Ansible 2.x playbook tasks`: https://docs.ansible.com/playbooks.html
.. _`Ansible inventories`: https://docs.ansible.com/ansible/intro_inventory.html
.. _Docker: https://www.docker.com/
.. _`Docker Compose`: https://docs.docker.com/compose/
.. _pytest: https://pytest.org/


Versioning
----------

goodplay will use `Semantic Versioning`_ when reaching v1.0.0.
Until then, the minor version is used for backwards-incompatible changes.

.. _`Semantic Versioning`: http://semver.org/


goodplay vs. Other Software
---------------------------

In this section we compare goodplay to some of the other software options
that are available to partly solve what goodplay can accomplish for you.

Ansible
~~~~~~~

Ansible_ itself comes bundled with some testing facilities mentioned in the
`Ansible Testing Strategies`_ documentation.
It makes a low-level ``assert`` module available which helps to verify that
some condition holds true, e.g. some output from a previous task which has
been stored in a variable contains an expected value.

Although it can be sometimes necessary to use something low-level as Ansible's
``assert``, goodplay enables you to use high-level modules for describing
your test cases.

Besides the actual testing, goodplay takes care of setting up and tearing down
the test environment as well as collecting the test results -- both being
something Ansible was not made for.

.. _`Ansible Testing Strategies`: https://docs.ansible.com/ansible/test_strategies.html


pytest-ansible
~~~~~~~~~~~~~~

`pytest-ansible`_ is as the name already implies a pytest_ plugin just like
goodplay.
But instead of being used for testing Ansible playbooks or roles, it provides
pytest fixtures that allow you to execute Ansible modules from your
Python-based tests.

.. _`pytest-ansible`: https://pypi.python.org/pypi/pytest-ansible


serverspec
~~~~~~~~~~

serverspec_ seems to be more targeted to assert hosts are in a defined
state.
In comparison to goodplay it allows you to run tests against single hosts
only and does not include test environment management.

.. _serverspec: http://serverspec.org


License
-------

goodplay is open source software released under the Apache License 2.0:

.. include:: ../../../LICENSE
