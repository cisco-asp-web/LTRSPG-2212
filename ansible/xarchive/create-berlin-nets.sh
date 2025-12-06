#!/bin/bash

# Berlin 1 
# Exit if already exists
ip link show berlin1-fe &>/dev/null && exit 0

# Create the bridge
ip link add name berlin1-fe type bridge
ip link set dev berlin1-fe up

# Add the IP address to the bridge for Berlin VMs default route
ip addr add 10.8.0.3/24 dev berlin1-fe

# Create the bridge
ip link add name berlin1-be type bridge
ip link set dev berlin1-be up


# Berlin 2
# Create the bridge
ip link add name berlin2-fe type bridge
ip link set dev berlin2-fe up

# Create the bridge
ip link add name berlin2-be type bridge
ip link set dev berlin2-be up

# Add the iptables rule to SNAT Berlin outbound traffic to the Internet
sudo iptables -t nat -A POSTROUTING -o ens160 -j MASQUERADE