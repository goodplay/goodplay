.. _contributing:

Contributor's Guide
===================

If you're reading this you're probably interested in contributing to
goodplay. First, we'd like to say: thank you! Open source projects
live-and-die based on the support they receive from others, and the fact that
you're even considering supporting goodplay is very generous of you.

This document lays out guidelines and advice for contributing to goodplay.
If you're thinking of contributing, start by reading this thoroughly and
getting a feel for how contributing to the project works.

The guide is split into sections based on the type of contribution you're
thinking of making, with a section that covers general guidelines for all
contributors.


All Contributions
-----------------

.. _early-feedback:

Get Early Feedback
~~~~~~~~~~~~~~~~~~

If you are contributing, do not feel the need to sit on your contribution until
it is perfectly polished and complete. It helps everyone involved for you to
seek feedback as early as you possibly can. Submitting an early, unfinished
version of your contribution for feedback in no way prejudices your chances of
getting that contribution accepted, and can save you from putting a lot of work
into a contribution that is not suitable for the project.

Contribution Suitability
~~~~~~~~~~~~~~~~~~~~~~~~

The project maintainer has the last word on whether or not a contribution is
suitable for goodplay. All contributions will be considered, but from time
to time contributions will be rejected because they do not suit the project.

If your contribution is rejected, don't despair! So long as you followed these
guidelines, you'll have a much better chance of getting your next contribution
accepted.


Code Contributions
------------------

Steps
~~~~~

When contributing code, you'll want to follow this checklist:

#. Fork the repository on GitHub.
#. Run the tests to confirm they all pass on your system. If they don't, you'll
   need to investigate why they fail. If you're unable to diagnose this
   yourself, raise it as a bug report by following the guidelines in this
   document: :ref:`bug-reports`.
#. Write tests that demonstrate your bug or feature. Ensure that they fail.
#. Make your change.
#. Run the entire test suite again, confirming that all tests pass *including
   the ones you just added*.
#. Send a GitHub Pull Request to the main repository's ``master`` branch.
   GitHub Pull Requests are the expected method of code collaboration on this
   project.

Code Review
~~~~~~~~~~~

Contributions will not be merged until they've been code reviewed. You should
implement any code review feedback unless you strongly object to it. In the
event that you object to the code review feedback, you should make your case
clearly and calmly. If, after doing so, the feedback is judged to still apply,
you must either apply the feedback or withdraw your contribution.


Documentation Contributions
---------------------------

Documentation improvements are always welcome! The documentation files live in
the ``docs/`` directory of the codebase. They're written in
`reStructuredText`_, and use `Sphinx`_ to generate the full suite of
documentation.

When contributing documentation, please attempt to follow the style of the
documentation files. This means a soft-limit of 79 characters wide in your text
files and a semi-formal prose style.

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx-doc.org/index.html


.. _bug-reports:

Bug Reports
-----------

Bug reports are hugely important! Before you raise one, though, please check
through the `GitHub issues`_, **both open and closed**, to confirm that the bug
hasn't been reported before. Duplicate bug reports are a huge drain on the time
of other contributors, and should be avoided as much as possible.

.. _GitHub issues: https://github.com/goodplay/goodplay/issues


Feature Requests
----------------

When you're missing some feature, feel free to raise a feature request
through the `GitHub issues`_. Please ensure beforehand that the same feature
request doesn't exist yet.
