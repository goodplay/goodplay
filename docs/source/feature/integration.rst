Integrating with Third Parties
==============================

GitLab CI
---------

`GitLab CI`_ is part of GitLab. You can use it for free on `GitLab.com`_.

.. code-block:: yaml

   ## .gitlab-ci.yml
   image: goodplay/goodplay

   services:
     - docker:dind

   test:
     script:
       - goodplay -v -s


.. _`GitLab CI`: https://about.gitlab.com/gitlab-ci/
.. _`GitLab.com`: https://gitlab.com/


Travis CI
---------

`Travis CI`_ is a continuous integration service that is available
to open source projects at no cost.

.. code-block:: yaml

   ## .travis.yml
   sudo: required
   dist: trusty

   language: python
   python: 2.7

   services:
     - docker

   before_install:
     # ensure apt-get cache is up-to-date
     - sudo apt-get -qq update

     # upgrade docker-engine to latest version
     - export DEBIAN_FRONTEND=noninteractive
     - sudo apt-get -qq -o Dpkg::Options::="--force-confnew" -y install docker-engine
     - docker version

   install:
     - pip install goodplay

   script:
     - goodplay -v

.. _`Travis CI`: https://travis-ci.org/


Jenkins CI
----------

To run on `Jenkins CI`_ you have to configure the following in your build job:

#. Under section **Build** choose **Add build step > Execute shell** with

   .. code-block:: bash

      pip install goodplay
      goodplay -v --junit-xml=junit.xml

#. Under section **Post-build Actions** choose
   **Add post-build action > Publish JUnit test result report** and set
   **Test report XMLs** to ``**/junit.xml``.

.. _`Jenkins CI`: https://jenkins-ci.org/


pytest
------

goodplay is built as a pytest_ plugin which is enabled by default.
Thus when running your other tests via ``py.test`` command-line interface,
pytest also runs the goodplay tests right beside them.

.. note::

   When running ``goodplay`` command-line interface only goodplay tests
   are considered.


.. _pytest: https://pytest.org/
