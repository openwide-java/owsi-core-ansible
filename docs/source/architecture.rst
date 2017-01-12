Architecture
============

This project enables owsi-core application deployment by providing both tools:

* ansible playbook to install application from a raw centos image
* vagrant plumbing so that ansible run can be launched on a virtualized
  environment (mainly for testing purpose)

Ansible
-------

Playbook structure
~~~~~~~~~~~~~~~~~~

The provided playbook install and configure the following components:

* utils: install common tools
* httpd: install httpd but skip configuration (so that apache user is created)
* postgresql: install pgdg repositories and postgresql packages (version is a
  configuration parameter)
* filesystem: initialize needed folders
* java: install needed jvm (version is a configuration parameter)
* ssl_selfsigned: generate a self-signed certificate for provided domain names
* httpd: generate a httpd configuration that targets a static resource folder
  and a tomcat instance (ajp proxy). HTTPS vhost is also generated. An apache
  status page, restricted to localhost access is configured.
* postgresql_cluster: initialize clusters and databases. Perform port and
  authentication configuration
* tomcat7: install catalina_base and catalina_home (tomcat version is a
  configuration parameter)
* war: deploy war

Role details
~~~~~~~~~~~~


