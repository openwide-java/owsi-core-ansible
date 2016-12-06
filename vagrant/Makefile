export VAGRANT_DEFAULT_PROVIDER=virtualbox

.PHONY: image
image:
	vagrant up $(M_VAGRANT_IMAGE)
	mkdir -p build
	vagrant ssh-config $(M_VAGRANT_IMAGE) > build/ssh_config_$(M_VAGRANT_IMAGE)

clean:
	vagrant destroy -f $(M_VAGRANT_IMAGE)
	rm -f build/ssh_config_$(M_VAGRANT_IMAGE)
