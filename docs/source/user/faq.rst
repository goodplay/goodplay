.. _faq:

Frequently Asked Questions
==========================

Is Docker required for running goodplay?
----------------------------------------

Although most people may use goodplay with Docker, it is absolutely fine to
run goodplay without Docker and instead run on localhost or against remote
hosts.
Just keep in mind that you need to take care on your own for setting up and
cleaning up your test environment in this case.


When is a test marked as passed, skipped, or failed?
----------------------------------------------------

An executed test always results in one of the following three test outcomes:
``passed``, ``skipped``, and ``failed``.
The following table shows the relation of Ansible *task results* of
*non-test tasks* and *test tasks* to the actual *test result*.

==========================  =================  ===========
task result                 non-test task      test task
==========================  =================  ===========
**ok**                      n/a                ``passed``
**ok (changed)**            n/a                ``failed``
**failed**                  ``global failed``  ``failed``
**failed (ignore failed)**  n/a                n/a
**skipped**                 n/a                ``skipped``
**unreachable host**        ``global failed``  ``failed``
**no hosts**                n/a                n/a
==========================  =================  ===========

These test results are collected for each host a task runs on.
At the end of a test task the results are combined to the final test outcome
according to the following rules in order:

#. If the task has been failed on one or more hosts test outcome is
   ``failed``.
#. If the task has been skipped on one or more hosts test outcome is
   ``skipped``.
#. Otherwise result in ``passed``.

.. note::

   - In case of a ``global failed`` this results in a failure with all
     subsequent tests being ``skipped``.

   - If all test tasks of a playbook are ``skipped`` this results in a failure.


Are test tasks free of side effects?
------------------------------------

It depends. Test tasks are run in *check mode* (and thus without side effects)
when supported by a module. If *check mode* is not supported, a module is run
in normal mode which can result in side effects (depending on a module's
functionality).

My shell/command test always fails. Why?
----------------------------------------

Since Ansible cannot know when a shell command has changed something, the shell/command task always sets `changed` to `true`.
This conflicts with goodplays assumption, that a task fails if it changed something.
To circumvent this, you need to tell Ansible that the shell command did not change using `changed_when`, for example::

  - name: "check java version"
     shell: java -version 2>&1 | grep -q '1.8.0_122'
     changed_when: False
     tags: test
