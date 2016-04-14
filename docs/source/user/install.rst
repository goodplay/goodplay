.. _installation:

Installation
============

This part of the documentation covers the installation of goodplay.


Installing Docker
-----------------

goodplay makes use of isolated containerized environments provided by Docker
for running your tests.

.. note::

   If you only require your tests to be run on localhost or some other
   test environment you manage on your own, you can skip Docker installation
   and continue with the next section.

As goodplay uses `Docker Compose`_ which enables you to use some great Docker
features like user-defined networks or embedded DNS server, we recommend to
run at least Docker version ``1.10.0``.
There are a lot of options when it comes to setting up a Docker host.

When running a Linux distribution with a recent kernel version, ``docker``
is most likely supported natively.
In this case the `installation process`_ will finish in a minute.

When running on Mac OS X, ``docker`` is not natively supported (yet).
Fortunately there is ``docker-machine`` available which lets you create
Docker hosts as virtual machine on your computer, on cloud providers,
or inside your own data center.
In this case `Docker Toolbox`_ helps you to setup everything you need.

Please make sure to read the official `Install Docker Engine`_ guide.

.. _`installation process`: https://docs.docker.com/linux/step_one/
.. _`Docker Compose`: https://docs.docker.com/compose/
.. _`Docker Toolbox`: https://www.docker.com/docker-toolbox
.. _`Install Docker Engine`: https://docs.docker.com/engine/installation/


Installing goodplay
-------------------

Installing latest released goodplay version is simple with pip_,
just run this in your terminal::

   $ pip install goodplay

Alternatively you can install the latest goodplay development version::

   $ pip install git+https://github.com/goodplay/goodplay.git#egg=goodplay

.. _pip: https://pip.pypa.io


Get the Code
------------

goodplay is actively developed on GitHub, where the code is
`always available <https://github.com/goodplay/goodplay>`_.

You can either clone the public repository::

    $ git clone https://github.com/goodplay/goodplay.git

Download the `tarball <https://github.com/goodplay/goodplay/archive/master.tar.gz>`_::

    $ curl -OL https://github.com/goodplay/goodplay/archive/master.tar.gz

Or, download the `zipball <https://github.com/goodplay/goodplay/archive/master.zip>`_::

    $ curl -OL https://github.com/goodplay/goodplay/archive/master.zip


Once you have a copy of the source, you can install it into your
site-packages easily::

    $ python setup.py install
