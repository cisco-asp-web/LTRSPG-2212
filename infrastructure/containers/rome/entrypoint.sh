#!/bin/bash
set -e

echo "--- Applying Network Configuration for Rome (.109) ---"

# --- 1. Global Interface Optimization ---
# Fixes "Caught tx_queue_len zero misconfig" and ensures MTU consistency
# This is required for stable IPv4 communication in Containerlab
echo "Optimizing interface queues and MTU..."
for intf in $(ls /sys/class/net | grep eth); do
    if [ "$intf" != "lo" ]; then
        ip link set "$intf" txqueuelen 1000 mtu 1500 || true
    fi
done

# --- 2. eth0: Management ---
if [[ $(ip addr show eth0 2>/dev/null) != *"172.20.6.109"* ]]; then
    echo "Configuring eth0..."
    ip addr flush dev eth0 || true
    ip addr add 172.20.6.109/24 dev eth0
    ip link set eth0 up
    ip route del default || true
    ip route add default via 172.20.6.1 dev eth0
else
    echo "eth0 already configured correctly by Containerlab."
fi

echo "nameserver 8.8.8.8" > /etc/resolv.conf

# --- 3. eth1: Configuration (Rome Side) ---
if ip link show eth1 > /dev/null 2>&1; then
    echo "Configuring eth1..."
    ip link set eth1 up
    # Wait for the interface to settle after Containerlab/XRd wiring
    sleep 1 

    ip addr flush dev eth1 || true
    ip addr add 10.107.1.2/24 dev eth1
    ip addr add fc00:0:107:1::2/64 dev eth1

    # Apply eth1 Routes
    ip route add 10.0.0.0/24 via 10.107.1.1 dev eth1 || true
    ip route add 10.101.1.0/24 via 10.107.1.1 dev eth1 || true
    ip route add 10.1.1.0/24 via 10.107.1.1 dev eth1 || true
    ip -6 route add fc00:0::/32 via fc00:0:107:1::1 dev eth1 || true
else
    echo "WARNING: eth1 not detected. Skipping eth1 config."
fi

# --- 4. eth2: Configuration (Rome Side) ---
if ip link show eth2 > /dev/null 2>&1; then
    echo "Configuring eth2..."
    ip link set eth2 up
    sleep 1

    ip addr flush dev eth2 || true
    ip addr add 10.107.2.2/24 dev eth2
    ip addr add fc00:0:107:2::2/64 dev eth2

    # Apply eth2 Routes
    ip route add 10.101.2.0/24 via 10.107.2.1 dev eth2 || true
    ip route add 10.200.0.0/24 via 10.107.2.1 dev eth2 || true
    ip -6 route add fc00:0:101:2::/64 via fc00:0:107:2::1 dev eth2 || true
else
    echo "WARNING: eth2 not detected. Skipping eth2 config."
fi

# --- 5. lo: Loopbacks ---
echo "Configuring Loopbacks..."
for addr in 20.0.0.1/32 30.0.0.1/32 40.0.0.1/32 50.0.0.1/32; do
    ip addr add $addr dev lo || true
done
ip addr add fc00:0:40::1/128 dev lo || true
ip addr add fc00:0:50::1/128 dev lo || true

echo "--- Network Configuration Complete ---"

# --- 6. Handover to SSHD ---
mkdir -p /run/sshd
exec "$@"
