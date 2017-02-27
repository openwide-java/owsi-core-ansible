Prerequisites
=============

You need a functional ansible and vagrant installation to run the
owsi-core-ansible playbook.

owsi-core-ansible is commonly used with the following released versions but
other versions may be working:

* make: 4.1
* vagrant: 1.8.1 / 1.9.1
* ansible: 2.2.0 (because of loop_control.label use)

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

If you use VirtualBox >= 5.1, you'll need on ubuntu to upgrade vagrant to a
newer version than the one available in 16.04 repositories. Vagrant provides
newer packages : https://www.vagrantup.com/downloads.html

Install ansible
###############

.. code-block:: bash
   
   sudo add-apt-repository ppa:ansible/ansible # ubuntu
   sudo apt-get install ansible # ubuntu

   sudo dnf install ansible # fedora

Sphinx (for documentation)
##########################

.. code-block:: bash

   sudo apt-get install build-essential python-virtualenv python-dev libffi-dev gcc # ubuntu
   sudo dnf groupinstal "Development Tools" # fedora
   sudo dnf install python-virtualenv python-devel libffi-devel gcc # fedora
   # at project root
   virtualenv venv
   . venv/bin/activate
   pip install sphinx sphinx_bootstrap_theme sphinx-autobuild

   # then each time you need to work with sphinx
   . venv/bin/activate
