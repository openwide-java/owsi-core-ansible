Prerequisites
=============

You need a functional ansible and vagrant installation to run the
owsi-core-ansible playbook.

owsi-core-ansible is commonly used with the following released versions but
other versions may be working:

* make: 4.1
* vagrant: 1.8.1
* ansible: 2.1.1

.. note::

   Fedora 24 and ubuntu 16.04 hosts' OS are known to be compatible with
   owsi-core-ansible. Following instructions may be modified to work with other
   hosts.

Misc
####

.. code-block:: bash

   sudo apt-get install make # ubuntu/debian 
   sudo dnf install make # fedora

Install vagrant
###############


.. code-block:: bash

   sudo apt-get install vagrant # ubuntu/debian
   sudo dnf install vagrant # fedora

Install ansible
###############

.. code-block:: bash
   
   sudo apt-get install ansible # ubuntu/debian
   sudo dnf install ansible # fedora
