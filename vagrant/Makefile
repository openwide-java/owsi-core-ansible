export VAGRANT_DEFAULT_PROVIDER=virtualbox

.PHONY: clean image image-ssh
image:
	vagrant up $(M_VAGRANT_IMAGE)
	mkdir -p build
	vagrant ssh-config $(M_VAGRANT_IMAGE) > build/ssh_config_$(M_VAGRANT_IMAGE)

image-ssh:
	vagrant up $(M_VAGRANT_IMAGE)
	vagrant ssh $(M_VAGRANT_IMAGE)

clean:
	vagrant destroy -f $(M_VAGRANT_IMAGE)
	rm -f build/ssh_config_$(M_VAGRANT_IMAGE)
