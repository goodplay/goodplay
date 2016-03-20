.. :changelog:

History
=======

0.6.0 (TBD - ACTIVE DEVELOPMENT)
--------------------------------


0.5.0 (2016-03-20)
------------------

Major Changes
~~~~~~~~~~~~~

* goodplay now requires at least Docker 1.10.0
* docker: make use of user-defined networks to isolate test environments
* docker: hosts can now resolve each other thanks to docker's embedded DNS server
* support use of local Ansible roles (``--use-local-roles``) during test run

Bug Fixes
~~~~~~~~~

* add missing ``ansible_user`` inventory variable in tests as this is required
  for latest docker connection plugin in Ansible
* fix junitxml support for ``pytest>=2.9.1``

Other Improvements
~~~~~~~~~~~~~~~~~~

* ease test writing by introducing ``smart_create`` helper
* speed-up tests by using ``gather_facts: no`` where possible
* docs: compare goodplay to other software
* add gitter chat badge
* explicitly disable Ansible retry files


0.4.1 (2016-01-22)
------------------

Major Changes
~~~~~~~~~~~~~

* repository moved to new organization on GitHub: goodplay/goodplay

Bug Fixes
~~~~~~~~~

* fix host vars getting mixed due to Ansible caches being kept as module state


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
