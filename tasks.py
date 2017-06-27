import invoke
from invoke import task
from invoke import Collection

import click
import subprocess
import getpass

import os
import re
import json
try:  # py3
    from shlex import quote
except ImportError:  # py2
    from pipes import quote

CONTEXT_SETTINGS = dict(
    max_content_width=120
)

@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass

@task
def _virtualenv(ctx, virtualenv_path=None):
    """
    Initialize a virtualenv folder.
    """
    ctx.virtualenv_path = os.path.dirname(__file__) + '/' + ctx.virtualenv_path
    virtualenv_path = virtualenv_path or ctx.virtualenv_path
    if not check_virtualenv(ctx, virtualenv_path):
        if not os.path.exists(os.path.dirname(virtualenv_path)):
            os.makedirs(os.path.dirname(virtualenv_path))
        ctx.run(' '.join(['virtualenv', virtualenv_path]))
        if not check_virtualenv(ctx, virtualenv_path):
            raise Exception('python install fails')

@task(pre=[_virtualenv])
def galaxy(ctx, virtualenv_path=None):
    """
    Install needed ansible dependencies with ansible-galaxy.
    """
    virtualenv_path = ctx.virtualenv_path;
    ctx.run(_vcommand(virtualenv_path, 'ansible-galaxy',
                      'install',
                      '-r', os.path.dirname(__file__) + '/requirements.yml',
                      '--roles-path', os.path.dirname(__file__) +'/dependencies/'))


@task
def _ansible(ctx, virtualenv_path=None, skip=None, version=None):
    """
    Install ansible inside a virtualenv folder.
    """
    skip = skip if (skip is not None) \
        else ctx.ansible.skip
    dependencies = ctx.dependencies
    if not skip:
        virtualenv_path = virtualenv_path or ctx.virtualenv_path
        package = ctx.ansible.package_name
        version = version or ctx.ansible.version
        _pip_package(ctx, package, version)
        for dependency in dependencies:
            _pip_package(ctx, dependency['name'],
                         dependency.get('version', None))
    else:
        print('ansible not managed (ansible.skip: yes)')


def _pip_package(ctx, package, version=None, virtualenv_path=None):
    """
    Install a pypi package (with pip) inside a virtualenv folder.
    """
    virtualenv_path = virtualenv_path or ctx.virtualenv_path
    if not check_pip(ctx, virtualenv_path, package, version):
        pip_install(ctx, virtualenv_path, package, version)
        if not check_pip(ctx, virtualenv_path, package, version):
            raise Exception('{} install fails'.format(package))


@task(pre=[_virtualenv, _ansible, galaxy])
def configure(ctx):
    """
    Trigger virtualenv, ansible initialization.

    All this tools are needed to handle ansible jobs and documentation
    generation.
    """
    pass


def _ansible_playbook(ctx, virtualenv_path=None, playbook=None,
                      extra_vars={}, ansible_args=''):
    """
    Run an ansible playbook
    """
    virtualenv_path = virtualenv_path or ctx.virtualenv_path
    _check_hosts(virtualenv_path)
    playbook = playbook or ctx.default_playbook
    playbook = os.path.dirname(__file__) + '/' + playbook
    os.environ['PATH'] = \
        os.path.join(virtualenv_path, 'bin') + ':' + os.environ['PATH']
    os.environ['ANSIBLE_CONFIG'] = os.path.dirname(__file__) + '/' + 'etc/ansible.cfg'
    os.environ['ANSIBLE_ROOT'] = os.path.dirname(__file__)
    args = [playbook]
    if ansible_args:
        args.extend(ansible_args.split(' '))
    if extra_vars:
        args.append('--extra-vars')
        args.append(quote(json.dumps(extra_vars)))
    ctx.run(_vcommand(virtualenv_path, 'ansible-playbook', *args), pty=True)

def _check_hosts(virtualenv_path):
    """
    Check if user present in hosts file
    """
    inventory_path = os.path.dirname(__file__) + '/inventory/hosts'
    hosts = subprocess.check_output([os.path.join(virtualenv_path, 'bin', 'ansible'), 'all', '-i', inventory_path, '--list-hosts'])
    if getpass.getuser() not in hosts:
        print 'Error : You must add your username (' + getpass.getuser() + ') in inventory/hosts'
        quit()


@task(
    name='list-hosts',
    pre=[configure],
    help={
        'limit': 'limit selected hosts by a pattern or a group; for example `-l qualification`'
    }
)
def ansible_list_hosts(ctx, limit=None):
    """
    List hosts from inventory
    """
    inventory_path = os.path.dirname(__file__) + '/inventory/hosts'
    ansible_cmd = ['ansible', 'all', '-i', inventory_path, '--list-hosts']
    if limit is not None:
        ansible_cmd.extend(['-l', limit])
    hosts = subprocess.check_output(ansible_cmd)
    print hosts


@task(
      name='run',
      pre=[configure],
      help={
          'virtualenv-path': 'custom virtualenv folder',
          'playbook': 'playbook to run',
          'check': 'run the ansible playbook with check option',
          'diff': 'run the ansible playbook with diff option',
          'ansible-args': 'additional ansible args',
          'extra-vars': 'extra ansible vars (json format)'
      }
)
def ansible_run(ctx, virtualenv_path=None, playbook=None, check=False, diff=False, extra_vars='', ansible_args=''):
    """
    Run an arbitrary ansible playbook.
    """
    extra_vars_parsed = {}
    ansible_args = ansible_args + ' ' + ctx.ansible_default_args
    if check:
        ansible_args = ansible_args + ' --check '
    if diff:
        ansible_args = ansible_args + ' --diff '
    if extra_vars:
        extra_vars_parsed = json.loads(extra_vars)
    _ansible_playbook(ctx, virtualenv_path=virtualenv_path, playbook=playbook,
                      ansible_args=ansible_args, extra_vars=extra_vars_parsed)


@task(name='up', pre=[configure])
def vagrant_up(ctx, environment='localhost', ansible_args=''):
    """
    Deploy a complete vagrant environment
    """
    _ansible_playbook(ctx, playbook='playbooks/vagrant-up.yml',
                      ansible_args=ansible_args + '--ask-become-pass',
                      extra_vars={'target_host': environment})


@task(name='destroy', pre=[configure])
def vagrant_destroy(ctx, environment='localhost', ansible_args=''):
    """
    Destroy a complete vagrant environment (erase vms)
    """
    _ansible_playbook(ctx, playbook='playbooks/vagrant-destroy.yml',
                      ansible_args=ansible_args,
                      extra_vars={'target_host': environment})


@task(name='halt', pre=[configure])
def vagrant_halt(ctx, ansible_args=''):
    """
    Halt a complete vagrant environment (shutdown vms, vms NOT erased)
    """
    _ansible_playbook(ctx, playbook='playbooks/vagrant-halt.yml',
                      ansible_args=ansible_args,
                      extra_vars={'target_host': environment})


@task(name='ssh', pre=[configure],
      help={'host': 'host to ssh to'})
def vagrant_ssh(ctx, host):
    """
    ssh in `host` vagrant vm
    """
    command_ssh = ' '.join([
        'ssh',
        '-F',
        os.path.join(os.path.dirname(__file__) + '/vagrant', host, 'ssh_config'),
        host
    ])
    ctx.run(command_ssh, pty=True)


def check_virtualenv(ctx, virtualenv_path):
    """
    Check if virtualenv is initialized in virtualenv folder (based on
    bin/python file).
    """
    r = ctx.run(' '.join([
        os.path.join(virtualenv_path, 'bin/python'),
        '--version'
    ]), warn=True, hide='both')
    return r.ok


def check_pip(ctx, virtualenv_path, package, version):
    """
    Check if a pypi package is installed in virtualenv folder.
    """
    r = ctx.run(' '.join([
        os.path.join(virtualenv_path, 'bin/pip'),
        'show',
        package
    ]), hide='both', warn=True)
    if not r.ok:
        # pip show package error - package is not here
        return False
    if version is None:
        # no version check needed
        return True
    # package here, check version
    m = re.search(r'^Version: (.*)$', r.stdout, re.MULTILINE)
    result = m is not None and m.group(1).strip() == version
    return result


def pip_install(ctx, virtualenv_path, package, version):
    """
    Install a pypi package in a virtualenv folder with pip.
    """
    pkgspec = None
    if version is None:
        pkgspec = package
    else:
        pkgspec = '{}=={}'.format(package, version)
    ctx.run(' '.join([
        os.path.join(virtualenv_path, 'bin/pip'),
        'install',
        pkgspec
    ]))


def _vcommand(virtualenv_path, command, *args):
    """
    Run a command from virtualenv folder.
    """
    cl = []
    cl.append(os.path.join(virtualenv_path, 'bin', command))
    cl.extend(args)
    return ' '.join(cl)


def _command(command, *args):
    """
    Run a command.
    """
    cl = []
    cl.append(os.path.join(command))
    cl.extend(args)
    return ' '.join(cl)

vagrant_ns = Collection('vagrant', vagrant_up, vagrant_destroy, vagrant_halt,
                                   vagrant_ssh)
ansible_ns = Collection('ansible', ansible_list_hosts, ansible_run)
ns = Collection(configure, galaxy, vagrant_ns, ansible_ns)
ns.configure({
    'ansible': {
        'package_name': 'ansible'
    },
    'dependencies': []
})

if __name__ == '__main__':
    cli()
