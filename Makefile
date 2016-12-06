
M_VAGRANT_IMAGE      = centos_7
M_ANSIBLE_CONFIG     = etc/ansible.conf
M_ANSIBLE_INVENTORY  = -i $(M_VAGRANT_IMAGE),
M_ANSIBLE_SSH_ARGS   = --ssh-common-args "-F vagrant/build/ssh_config_$(M_VAGRANT_IMAGE)"
M_ANSIBLE_VERBOSITY  = $(or $(ANSIBLE_VERBOSITY),)
export

.PHONY: vagrant-image
vagrant-image:
	@make -C vagrant image

.PHONY: clean-vagrant
clean-vagrant:
	@make -C vagrant clean

test-%: vagrant-image
	ANSIBLE_CONFIG=$(M_ANSIBLE_CONFIG) ansible-playbook \
		$(M_ANSIBLE_VERBOSITY) \
		$(M_ANSIBLE_SSH_ARGS) \
		$(M_ANSIBLE_INVENTORY) \
		tests/$*.yml
