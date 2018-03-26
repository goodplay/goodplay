Release Process
===============

The following steps describe the release process which is only expected to be
executed by maintainers of goodplay.

#. Ensure you are on ``master`` branch.

#. Update version number in ``goodplay/__init__.py`` and
   ``docs/source/conf.py``.
   Keep in mind that this needs to follow `Semantic Versioning`_.

#. Update changelog in ``HISTORY.rst``.

#. Commit the version change via:

   .. code-block:: bash

      $ git add goodplay/__init__.py
      $ git add docs/source/conf.py
      $ git add HISTORY.rst
      $ git commit -m 'bump version to X.Y.Z'

#. Tag the recent commit:

   .. code-block:: bash

      $ git tag vX.Y.Z

#. Push the ``master`` branch and version tag ``vX.Y.Z`` to GitHub:

   .. code-block:: bash

      $ git push origin master
      $ git push origin vX.Y.Z

#. Publish package on PyPI_ (as `goodplay package`_):

   .. code-block:: bash

      $ make publish

#. `Create new release`_ on GitHub.

   - As *Tag version* choose the just pushed version tag ``vX.Y.Z``.
   - Name the *Release title* after the version tag ``vX.Y.Z``.
   - *Describe the release* by reusing the version's changelog text from
     ``HISTORY.rst``.

.. _`Semantic Versioning`: http://semver.org/
.. _PyPI: https://pypi.python.org/pypi
.. _`goodplay package`: https://pypi.python.org/pypi/goodplay
.. _`Create new release`: https://github.com/goodplay/goodplay/releases/new
