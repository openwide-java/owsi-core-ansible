#! /bin/bash

set -e

if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
	# file is sourced
	echo "Modifying PATH env variable"
	PATH=~/.bin:$PATH
	echo "PATH=$PATH"
	return;
fi

echo -e "\ncheck virtualenv installation\n"
if [ -f /usr/bin/apt-get ]; then
	sudo apt-get install python-virtualenv libssl-dev python-dev gcc libxml2-dev python-lxml
elif [ -f /usr/bin/yum ]; then
	sudo yum install -y python-virtualenv python2-virtualenv openssl-devel python-devel gcc libxml2-devel python-lxml
elif [ -f /usr/bin/dnf ]; then
	sudo dnf install python2-virtualenv openssl-devel python-devel gcc libxml2-devel python-lxml
fi

mkdir -p .builddir/
mkdir -p ~/.bin
rm -rf .builddir/invoke
virtualenv .builddir/invoke

echo -e "\ninstall invoke\n"
./.builddir/invoke/bin/pip install invoke
./.builddir/invoke/bin/pip install click==6.0

here=$( readlink -f . )
python=$( readlink -f ./.builddir/invoke/bin/python )

echo -e "\nsymlink invoke\n"
if [ -h ~/.bin/invoke ]; then
	if [ "$( readlink ~/.bin/invoke )" != "$( readlink -f ./.builddir/invoke/bin/invoke )" ]; then
		echo -e "\n~/.bin/invoke already exists and does not target $( readlink -f ./.builddir/invoke/bin/invoke ) ; install fails\n"
		exit 1
	fi
else
	ln -s "$( readlink -f ./.builddir/invoke/bin/invoke)" ~/.bin/invoke
fi

if ! [[ "$PATH" =~ "$HOME/.bin" ]]; then
	echo -e "\n~/.bin/invoke installed but ~/.bin is not in your \$PATH\n"
	echo -e "\nrun \". bootstrap.sh\" to modify you PATH variable\n"
	exit 1
fi

echo -e "\nbootstrap done\n"
