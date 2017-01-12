Quick run
=========

.. code-block:: bash

   # in default.yml, modify war_application_war_src to target an existing war to deploy
   sed -i -e 's@war_application_war_src:.*@war_application_war_src: /mypath/to/application.war@' tests/war.yml
   # move at project root and initialize vagrant image
   make test-war
   # obtain a guest ssh shell
   make vagrant-image-ssh
   # obtain local ip-adress (probably 192.168....)
   ifconfig
   # logout ^D
   sudo vim /etc/hosts
   # add an entry IP cas.dev and save file
   echo -e "\n<IP> cas.dev" | tee -a /etc/hosts
   # open your browser
   xdg-open https://cas.dev/cas
