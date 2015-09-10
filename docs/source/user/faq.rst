.. _faq:

FAQ
===

When gets a test marked as passed, skipped, or failed?
------------------------------------------------------

====================================  =============  =========
task result                           non-test task  test task
====================================  =============  =========
**runner_on_ok**                      n/a            passed
**runner_on_failed**                  global failed  failed
**runner_on_failed (ignore failed)**  n/a            n/a
**runner_on_skipped**                 n/a            skipped
**runner_on_unreachable**             global failed  failed
**runner_on_no_hosts**                n/a            n/a
====================================  =============  =========

These results are collected for each host a task runs on.
At the end of a test task the results are combined to the final test outcome
according to the following rules:

1. If the task has been failed on one or more hosts test outcome is
   ``failed``.
2. If the task has been skipped on one or more hosts test outcome is
   ``skipped``.
3. Otherwise result in ``passed``.
