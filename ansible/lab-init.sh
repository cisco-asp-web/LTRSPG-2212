#!/bin/bash

echo "define berlin-net"
virsh net-define ../lab_1/config/berlin-vm/berlin-net.xml
virsh net-start berlin-net
echo "add brctl"
sudo brctl addbr berlin-net
echo "set berlin-net up"
sudo ip link set berlin-net up
echo "add addr"
sudo ip addr add 198.18.4.3/24 dev berlin-net
echo "add iptables"
sudo iptables -t nat -A POSTROUTING -o ens160 -j MASQUERADE 

echo "define berlin"
virsh define ../lab_1/config/berlin-vm/berlin.xml
echo "start berlin"
virsh start berlin

brctl show 
ifconfig berlin-net
sudo iptables -t nat --list | grep MASQUERADE
virsh list --all

cd LTRSPG-2212/lab_5/scripts/xrd-network/
python3 add_meta_data.py
cd ~/

