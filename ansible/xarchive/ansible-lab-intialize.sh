#!/bin/bash

echo "startup dCloud script launched at: " > /home/dcloud/deploy.log

date >> /home/dcloud/deploy.log
whoami >> /home/dcloud/deploy.log

echo "startup dCloud script launched at: " > /home/cisco/deploy.log

date >> /home/cisco/deploy.log
whoami >> /home/cisco/deploy.log

ansible-playbook -e "ansible_user=dcloud ansible_ssh_pass=C1sco12345 ansible_sudo_pass=C1sco12345" \
  /home/dcloud/LTRSPG-2212/ansible/dcloud_startup_playbook.yaml -v >> /home/dcloud/deploy.log
