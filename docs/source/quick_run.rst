Quick run
=========

The *tests/war.yml* playbook provided in repository install a cas.war webapp in
a running tomcat 7 instance. You can modify this file to deliver an alternative
war package.

.. code-block:: bash

   # move at project root and initialize vagrant image
   make test-war
   # obtain a guest ssh shell
   make vagrant-image-ssh
   # obtain local ip-adress (probably 192.168....)
   ifconfig
   # logout vagrant guest: ctrl+d
   # add an entry IP cas.dev and save file
   echo -e "\n<IP> cas.dev" | tee -a /etc/hosts
   # open your browser
   xdg-open https://cas.dev/cas
   # you need to accept self-signed certificate
