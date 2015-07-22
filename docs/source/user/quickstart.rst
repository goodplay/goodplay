.. _quickstart:

Quickstart
==========

Eager to get started? This page gives a good introduction in how to get started
with goodplay.

.. code-block:: yaml

   ---
   - hosts: default
     become: yes

     roles:
       - name: crond


   - hosts: default
     become: yes

     tasks:
       - name: assert crond service is running
         service:
           name: crond
           state: started
         tags: test
