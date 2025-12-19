#!/bin/bash
set -e

echo "--- Applying Network Configuration for London (.108) ---"

# --- 1. Global Interface Optimization ---
# Fixes "Caught tx_queue_len zero misconfig" and ensures MTU consistency
echo "Optimizing interface queues and MTU..."
for intf in $(ls /sys/class/net | grep eth); do
    if [ "$intf" != "lo" ]; then
        ip link set "$intf" txqueuelen 1000 mtu 1500 || true
    fi
done

# --- 2. eth0: Management ---
CURRENT_IP=$(ip -4 addr show eth0 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n 1)

if [ "$CURRENT_IP" != "172.20.6.108" ]; then
    echo "Updating eth0 to 172.20.6.108..."
    ip addr flush dev eth0 || true
    ip addr add 172.20.6.108/24 dev eth0
    ip link set eth0 up
    ip route del default || true
    ip route add default via 172.20.6.1 dev eth0
else
    echo "eth0 already configured correctly."
fi

echo "nameserver 8.8.8.8" > /etc/resolv.conf

# --- 3. eth1: Configuration (London Data Plane) ---
if ip link show eth1 > /dev/null 2>&1; then
    echo "Configuring eth1..."
    ip link set eth1 up
    # Wait for the interface to settle after Containerlab/XRd wiring
    sleep 1 

    ip addr flush dev eth1 || true
    ip addr add 10.101.1.2/24 dev eth1
    ip addr add fc00:0:101:1::2/64 dev eth1

    # IPv4 Routes via London Gateway (10.101.1.1)
    ip route add 10.0.0.0/24 via 10.101.1.1 dev eth1 || true
    ip route add 10.107.1.0/24 via 10.101.1.1 dev eth1 || true
    ip route add 10.1.1.0/24 via 10.101.1.1 dev eth1 || true
    # IPv6 Routes
    ip -6 route add fc00:0::/32 via fc00:0:101:1::1 dev eth1 || true
else
    echo "WARNING: eth1 not detected."
fi

# --- 4. eth2: Configuration (Future-Proofing) ---
if ip link show eth2 > /dev/null 2>&1; then
    echo "Configuring eth2..."
    ip link set eth2 up
    sleep 1
    
    ip addr flush dev eth2 || true
    # Current topology doesn't specify London eth2 IPs, 
    # but we fix the queue/state here just in case.
else
    echo "eth2 not present, skipping."
fi

echo "--- Network Configuration Complete ---"

# --- 5. Handover to SSHD ---
mkdir -p /run/sshd
exec "$@"
