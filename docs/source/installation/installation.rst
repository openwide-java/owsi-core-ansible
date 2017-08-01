############
Installation
############


Les commandes qui suivent nécessitent l'installation d'invoke : :ref:`installation-invoke`

Les commandes suivantes peuvent nécessiter d'être lancées par un utilisateur possédant déjà les accès SSH avant d'être lancées par un nouvel utilisateur. Voir :ref:`ssh_keys`

**********************************
Environnement vagrant / virtualbox
**********************************

.. code-block:: bash

  invoke all -h project-name.vagrant


*******************************************
Sur openwidesi-vm-recettejava.accelance.net
*******************************************

.. code-block:: bash

  invoke all -h virtual-machine.address

.. _ssh_keys:

********
Clés SSH
********

Les clés SSH peuvent être déployées par le provisionning. Pour cela, ajouter la clé dans le fichier ``inventory/group_vars/all/authorized_keys.yml``

Référencer ensuite la clé à déployer dans les ``host_vars/*`` ou ``group_vars/*`` souhaités, variable (liste) ``playbook_ssh_authorized_keys``.

Fichier des clés:

.. literalinclude:: ../../../inventory/group_vars/all/authorized_keys.yml
  :caption: déclaration des clés (les clés déployées sont contrôlées par ``playbook_ssh_authorized_keys``)
