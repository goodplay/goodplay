.. :changelog:

History
=======

0.5.0 (TBD - ACTIVE DEVELOPMENT)
--------------------------------


0.4.0 (2016-01-13)
------------------

Major Changes
~~~~~~~~~~~~~

* add support for testing against defined Docker environment
* make latest Ansible 2.0 release candidate install automatically
* massive documentation refactorings, now available under https://docs.goodplay.io/
* introduce command line interface: goodplay
* drop Ansible 1.9.x support to move things forward

Bug Fixes
~~~~~~~~~

* fix goodplay plugin missing when running Ansible

Internal Changes
~~~~~~~~~~~~~~~~

* switch from traditional Code Climate to new Code Climate Platform
* disable use_develop in tox.ini to more closely match a real user's environment
* refactor code to have sarge integrated at a single point


0.3.0 (2015-09-07)
------------------

Major Changes
~~~~~~~~~~~~~

* add support for Ansible role testing
* add support for auto-installing Ansible role dependencies (hard dependencies)
* add support for auto-installing soft dependencies

Bug Fixes
~~~~~~~~~

* fix test failing when previous non-test task has been changed
* fix failing non-test task after all completed test tasks not being reported as failure

Internal Changes
~~~~~~~~~~~~~~~~

* use ansible-playbook subprocess for collecting tests as Ansible does
  not provide an official Python API and Ansible internals are more likely
  to be changed
* various code refactorings based on Code Climate recommendations
* switch to Travis CI for testing as it now supports Docker


0.2.0 (2015-08-24)
------------------

* initial implementation of Ansible v1 and v2 test collector and runner


0.1.0 (2015-07-22)
------------------

* first planning release on PyPI
