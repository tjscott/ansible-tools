#!/usr/bin/env python

# -----------------------------------------------------------------------------
# Project           :   ansible-tools/ssh-keyexchange.py
# -----------------------------------------------------------------------------
# Author            :   Tristan Scott                  <tristan@scott-mail.net>
# License           :   GPL v3
# -----------------------------------------------------------------------------
# Creation date     :   2013-07-22
# Last mod.         :   2013-07-22
# -----------------------------------------------------------------------------

# SSH key exchange for systems in the ansible hosts file
# Requires Paramiko

# Modify these lines for your environment:
username = 'root'
passwords = ['rootpassword','alternativerootpassword']
hostsfile = '/home/config/prod/ansible_hosts'
pubkeyfile = '~/.ssh/id_rsa.pub'


########

import os
import sys
import paramiko


def deploy_key(key, server, username, password):
    # Set up SSH library, automatically add remote host keys
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print('Attempting to log into %s as %s' % (server, username))
        ssh.connect(server, username=username, password=password)
    except:
        print('Connection to %s failed for username %s/%s' % (server, username))
        return

    print('Connected to %s' % server)
    ssh.exec_command('if [ ! -d ".ssh" ]; then mkdir -p ~/.ssh/')                       # use bash to create ssh config dir if it does not exist
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('cat ~/.ssh/authorized_keys')  # ask the host to print the contents of the authorized_keys file
    authorized_keys = ssh_stdout.readlines()                                            # obtain the file conents
    if any(key in line for line in authorized_keys):
        print('Found key for %s@%s, not adding it' % (username, server))
    else:
        print('Key not found for %s@%s, adding it' % (username, server))
        ssh.exec_command('echo "%s" >> ~/.ssh/authorized_keys' % key)
        ssh.exec_command('chmod 644 ~/.ssh/authorized_keys')
        ssh.exec_command('chmod 700 ~/.ssh/')
    ssh.close()



# Retrieve hosts from Ansible hostsfile
hostsfile = os.path.expanduser(hostsfile)  # expand the path (Python doesn't like ~)
hostlist = [ ]
try:
    f = open(hostsfile, 'r')
    for line in f:
        if not line.strip().startswith(('[','#')) and len(line.strip()) != 0:
            hostlist.append(line.rstrip("\r\n"))
    f.close()
except:
    sys.stderr.write('Cannot open hosts file: %s. Exiting.\n' % hostsfile)
    sys.exit(1)


# Retrieve local rsa public key
pubkeyfile = os.path.expanduser(pubkeyfile)  # expand the path (Python doesn't like ~)
try:
    f = open(pubkeyfile, 'r')
    key = f.read().strip()
    f.close()
except:
    sys.stderr.write('Cannot read from key file: %s. Exiting\n' % pubkeyfile)
    sys.exit(1)


# Confirm, then start the key exchange
print('The following hosts will have the public key from this user and host added:')
for host in hostlist:
    print(host)
confirm = raw_input('Do you wish to proceed? ')
if confirm.startswith('y'):
    for host in hostlist:
        for password in passwords:
            deploy_key(key, host, username, password)


