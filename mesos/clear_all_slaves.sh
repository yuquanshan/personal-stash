#!/bin/bash

# supposed to run on master
# first set passphraseless ssh from master to slaves (copy slaves' pub-key to
# master's ~/.ssh/authorized_keys) 
# second you need either 1. specify slaves' ip addresses in /etc/slave-hosts or
# 2. specify slaves' hostnames in /etc/slave-hosts and hostname-ip mapping in
# /etc/hosts

slvs=$(cat /etc/slave-hosts)

for slv in $slvs
  do
    ssh ubuntu@${slv} 'MESOS_PID=$(pgrep -f "lt-mesos-*");sudo kill ${MESOS_PID}'
    ssh ubuntu@${slv} 'sudo rm -R /var/lib/mesos*'
  done
