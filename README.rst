goodplay
========

|build-status| |version| |docs| |license| |code-climate| |code-coverage| |dependencies-status| |donate|

goodplay is an Apache2-licensed test framework for testing Ansible 2.x roles
and playbooks as well as running full integration tests for your software.

.. |build-status| image:: https://img.shields.io/travis/benjixx/goodplay/master.svg
    :alt: Build Status
    :scale: 100%
    :target: https://travis-ci.org/benjixx/goodplay

.. |code-climate| image:: https://img.shields.io/codeclimate/github/benjixx/goodplay.svg
    :alt: Code Climate
    :scale: 100%
    :target: https://codeclimate.com/github/benjixx/goodplay

.. |code-coverage| image:: https://img.shields.io/codecov/c/github/benjixx/goodplay.svg
    :alt: Code Coverage
    :scale: 100%
    :target: https://codecov.io/github/benjixx/goodplay

.. |docs| image:: https://img.shields.io/badge/docs-latest-blue.svg
    :alt: Documentation
    :scale: 100%
    :target: https://docs.goodplay.io/

.. |donate| image:: https://img.shields.io/badge/donate_via_paypal-$5-yellow.svg
    :alt: Donate via PayPal
    :scale: 100%
    :target: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=SDQVYJQBMHVX2

.. |license| image:: https://img.shields.io/pypi/l/goodplay.svg
    :alt: License
    :scale: 100%
    :target: https://github.com/benjixx/goodplay/blob/master/LICENSE

.. |dependencies-status| image:: https://img.shields.io/requires/github/benjixx/goodplay.svg?label=dependencies
    :alt: Dependencies Status
    :scale: 100%
    :target: https://requires.io/github/benjixx/goodplay/requirements/

.. |version| image:: https://img.shields.io/pypi/v/goodplay.svg
    :alt: Version
    :scale: 100%
    :target: https://pypi.python.org/pypi/goodplay


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


Installation
------------

Installing goodplay is simple with pip_, just run this in your terminal:

.. code-block:: bash

    $ pip install goodplay

.. _pip: https://pip.readthedocs.org/


Documentation
-------------

Documentation is available at https://docs.goodplay.io/.


Roadmap
-------

- better error messages, without the clutter
- support to keep test environment running for debugging purposes
- support full-fledged virtual machine within a Docker container (see `RancherVM`_)

.. _`RancherVM`: https://github.com/rancher/vm


Contributing
------------

#. Check for open issues or open a fresh issue to start a discussion around a
   feature idea or bug.
#. Fork `the repository`_ on GitHub to start making your changes to the
   **master** branch (or branch off of it).
#. Write a test which shows that the bug was fixed or that the feature works
   as expected.
#. Send a pull request. Make sure to add yourself to AUTHORS_.

Just don't forget to check out our `CONTRIBUTING`_ guidelines — it includes
few technical details that will make the process a lot smoother.

.. _`the repository`: https://github.com/benjixx/goodplay
.. _AUTHORS: https://github.com/benjixx/goodplay/blob/master/AUTHORS.rst
.. _CONTRIBUTING: https://github.com/benjixx/goodplay/blob/master/CONTRIBUTING.rst
