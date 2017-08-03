import invoke
from invoke import task
from invoke import Collection

import click
import subprocess
import getpass

import os
import re
import shlex
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


@task
def _sphinx(ctx, virtualenv_path=None, skip=None, version=None):
    """
    Install sphinx inside a virtualenv folder.
    """
    skip = skip if (skip is not None) \
        else ctx.sphinx.skip
    dependencies = ctx.sphinx.dependencies
    if not skip:
        virtualenv_path = virtualenv_path or ctx.virtualenv_path
        package = ctx.sphinx.package_name
        version = version or ctx.sphinx.version
        _pip_package(ctx, package, version)
        for dependency in dependencies:
            _pip_package(ctx, dependency['name'],
                         dependency.get('version', None))
    else:
        print('sphinx not managed (sphinx.skip: yes)')


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


@task(pre=[_virtualenv, _sphinx, _ansible, galaxy])
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
    virtualenv_path = ctx.virtualenv_path
    inventory_path = os.path.dirname(__file__) + '/inventory/hosts'
    ansible_args = ['all', '-i', inventory_path, '--list-hosts']
    if limit is not None:
        ansible_args.extend(['-l', limit])
    hosts = subprocess.check_output(shlex.split(_vcommand(virtualenv_path, 'ansible', *ansible_args), False, True))
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


@task(name='all', pre=[configure])
def all(ctx, host, ansible_args='', build_owsi_core=False, force_build=False, skip_build=False):
    """
    Deploy all on provided host
    """
    extra_vars = {'playbook_host': host, 'playbook_build_owsi_core': build_owsi_core, 'playbook_force_build': force_build, 'playbook_skip_build': skip_build}
    _ansible_playbook(ctx, playbook='playbooks/all.yml',
                      ansible_args=ansible_args + ' --ask-become-pass',
                      extra_vars=extra_vars)

@task(name='up', pre=[configure])
def vagrant_up(ctx, environment='localhost', ansible_args=''):
    """
    Deploy a complete vagrant environment
    """
    _ansible_playbook(ctx, playbook='playbooks/vagrant-up.yml',
                      ansible_args=ansible_args + ' --ask-become-pass',
                      extra_vars={'target_host': 'vagrant'})


@task(name='destroy', pre=[configure])
def vagrant_destroy(ctx, environment='localhost', ansible_args=''):
    """
    Destroy a complete vagrant environment (erase vms)
    """
    _ansible_playbook(ctx, playbook='playbooks/vagrant-destroy.yml',
                      ansible_args=ansible_args,
                      extra_vars={'target_host': 'vagrant'})


@task(name='halt', pre=[configure])
def vagrant_halt(ctx, ansible_args=''):
    """
    Halt a complete vagrant environment (shutdown vms, vms NOT erased)
    """
    _ansible_playbook(ctx, playbook='playbooks/vagrant-halt.yml',
                      ansible_args=ansible_args,
                      extra_vars={'target_host': 'vagrant'})


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


def _docs_makefile(target, ctx, virtualenv_path=None):
    """
    Trigger a sphinx Makefile target. Used to delegate all documentation jobs to
    original sphinx Makefile.
    """
    virtualenv_path = virtualenv_path or ctx.virtualenv_path
    os.environ['PATH'] = \
        ':'.join([
            os.path.abspath(os.path.join(virtualenv_path, 'bin')),
            os.environ['PATH']])
    args = ['make', '-C', 'docs', target]
    ctx.run(' '.join(args), pty=True)


@task(name='build', pre=[configure])
def docs_build(ctx, virtualenv_path=None):
    """
    Rebuild documentation.
    """
    _docs_makefile('html', ctx, virtualenv_path)


@task(name='clean', pre=[configure])
def docs_clean(ctx, virtualenv_path=None):
    """
    Clean generated documentation.
    """
    _docs_makefile('clean', ctx, virtualenv_path)


@task(name='live', pre=[docs_build, configure])
def docs_live(ctx, virtualenv_path=None):
    """
    Live build of documentation on each modification. Open a browser with a
    local server to serve documentation. Opened page is reloaded each time
    documentation is generated.
    """
    virtualenv_path = virtualenv_path or ctx.virtualenv_path
    os.environ['PATH'] = \
        ':'.join([
            os.path.abspath(os.path.join(virtualenv_path, 'bin')),
            os.environ['PATH']])
    command = ' '.join([
        'sphinx-autobuild',
        '-B',
        '--ignore', '"*.swp"',
        '--ignore', '"*.log"',
        '--ignore', '"*~"',
        '--ignore', '"*~"',
        '-b', 'html',
        os.path.join(os.path.dirname(__file__), 'docs/source'),
        os.path.join(os.path.dirname(__file__), 'docs/build/html')
    ])
    ctx.run(command, pty=True)

@task(name='publish', pre=[docs_clean, docs_build, configure])
def docs_publish(ctx, virtualenv_path=None):
    """
    Push generated documentation to online website.

    Rsync url configured by docs_rsync_target (invoke.yaml)
    """
    host_path = ctx.config.docs_rsync_target.split(':')
    host = host_path[0]
    path = host_path[1]
    if not path:
        raise Error('path null or empty')
    virtualenv_path = virtualenv_path or ctx.virtualenv_path
    if not ctx.config.docs_rsync_target:
        raise Error('Missing docs_rsync_target in configuration')
    command = ' '.join([
        'rsync',
        '-avzr',
        '--delete',
        '--omit-dir-times',
        '--no-owner',
        '--no-group',
        '--no-perms',
        os.path.join(os.path.dirname(__file__), 'docs/build/html/'),
        '"{}"'.format(ctx.config.docs_rsync_target)
    ])
    if not ctx.config.grp_exec:
        raise Error('Missing grp_exec in configuration')
    command_ssh = ' '.join([
        'ssh',
        '"{}"'.format(ctx.config.docs_rsync_target.split(':')[0]),
        'find',
        '"{}"'.format(ctx.config.docs_rsync_target.split(':')[1]),
        '-user', '$USER', '-exec', 'chgrp', '-R', ctx.config.grp_exec, '{}', ' \\\\\\;'
    ])
    ctx.run(command, pty=True)
    ctx.run(command_ssh, pty=True)
    if os.path.exists('/usr/bin/xdg-open'):
        ctx.run('{} {}'.format('/usr/bin/xdg-open', ctx.config.docs_online_path))


docs_ns = Collection('docs', docs_build, docs_live, docs_publish, docs_clean)
vagrant_ns = Collection('vagrant', vagrant_up, vagrant_destroy, vagrant_halt,
                                   vagrant_ssh)
ansible_ns = Collection('ansible', ansible_list_hosts, ansible_run)
ns = Collection(configure, galaxy, vagrant_ns, ansible_ns, docs_ns, all)
ns.configure({
    'ansible': {
        'package_name': 'ansible'
    },
    'sphinx': {
        'package_name': 'sphinx',
        'dependencies': [
            { 'name': 'sphinx-bootstrap-theme' },
            { 'name': 'sphinx-autobuild' }
        ]
    },
    'recommonmark': {
        'package_name': 'recommonmark'
    },
    'dependencies': []
})

if __name__ == '__main__':
    cli()
