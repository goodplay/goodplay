.. :changelog:

History
=======

0.10.0 (2018-03-26)
-------------------

Major Changes
~~~~~~~~~~~~~

* add support for Ansible 2.5, drop support for Ansible 2.2
* require ``pytest>=3.5.0`` due to a change in their nodeid calculation


0.9.1 (2018-01-15)
------------------

Minor Changes
~~~~~~~~~~~~~

* report appropriate build error message when building from docker-compose
* fix warning "Module already imported so cannot be rewritten: goodplay"


0.9.0 (2017-12-25)
------------------

Minor Changes
~~~~~~~~~~~~~

* when using docker-compose.yml files in tests with referenced Dockerfiles,
  a build is triggered before bringing up the containers (NOT attempting to
  pull the latest base image as image might be only available locally)


0.8.1 (2017-12-19)
------------------

Minor Changes
~~~~~~~~~~~~~

* require ``docker-compose>=1.18.0`` due to a method signature change
* when using docker-compose.yml files in tests with referenced Dockerfiles,
  a build is triggered before bringing up the containers (always attempting
  to pull the latest base image)


0.8.0 (2017-10-15)
------------------

Major Changes
~~~~~~~~~~~~~

* add support for Ansible 2.2, 2.3, and 2.4, drop support for Ansible 2.1
* add support for Docker 1.12 and greater, drop support for Docker 1.11 and below
* add support for Python 3.6, now effectively supporting Python 2.7 and 3.6
* update to pytest 3
* provide Docker image ``goodplay/goodplay``

Minor Changes
~~~~~~~~~~~~~

* mention GitLab CI support in the docs

Internal Changes
~~~~~~~~~~~~~~~~

* improve Python-Ansible combinations that are tested on Travis CI


0.7.0 (2016-06-18)
------------------

Major Changes
~~~~~~~~~~~~~

* support ``become_user`` with Docker's native user management when running
  privilege escalation task against Docker Compose environment thus ``sudo``
  is not required in a Docker container anymore; this may change in a future
  version once Ansible supports ``su`` with Docker connection plugin
* drop support for ``ansible==2.0.x``, now require ``ansible>=2.1.0``

Bug Fixes
~~~~~~~~~

* fix issue with using local Ansible roles (``--use-local-roles``)
* fix wait_for test task that timeouts or otherwise fails resulting in
  global fail

Internal Changes
~~~~~~~~~~~~~~~~

* skip Docker-related tests when Docker is not available
* run Travis CI tests against latest two Docker minor versions,
  each with latest patch version
* add tests for automatic check mode usage when using a custom module
  that supports check mode


0.6.0 (2016-04-28)
------------------

Major Changes
~~~~~~~~~~~~~

* use Docker Compose for defining environments instead of reinventing the
  wheel, thus bringing you all the latest and greatest features of
  Docker Compose (e.g. running from Dockerfile, custom networks, custom
  entrypoints, shared volumes, and more)
* support running any test playbook (not only Ansible role playbooks) against
  multiple environments
* test tasks now run in check mode when supported by module
* remove ``goodplay_image`` and ``goodplay_platform`` support from inventory
  files
* remove ``.goodplay.yml`` support as it has only been used for defining
  platform-name-to-docker-image mapping which is now handled by Docker Compose

Minor Changes
~~~~~~~~~~~~~

* now depend on ``pytest>=2.9.1,<3``

Other Improvements
~~~~~~~~~~~~~~~~~~

* fresh goodplay logo
* do not display traceback for goodplay failures


0.5.0 (2016-03-20)
------------------

Major Changes
~~~~~~~~~~~~~

* goodplay now requires at least Docker 1.10.0
* docker: make use of user-defined networks to isolate test environments
* docker: hosts can now resolve each other thanks to Docker's embedded DNS server
* support use of local Ansible roles (``--use-local-roles``) during test run

Bug Fixes
~~~~~~~~~

* add missing ``ansible_user`` inventory variable in tests as this is required
  for latest Docker connection plugin in Ansible
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
