#!/bin/bash

# Start bridges
#!/usr/bin/env bash
set -euo pipefail

BRIDGES=(
  "london-vm-00-fe" "london-vm-01-fe" "london-vm-02-fe"
  "london-vm-00-be" "london-vm-01-be" "london-vm-02-be"
)

for b in "${BRIDGES[@]}"; do
  ip link add name "$b" type bridge 2>/dev/null || true
  ip link set "$b" up
done

# Start london-vm-00 Control Plane VM
virsh start london-vm-00

# Start london-vm-01 Worker VM
virsh start london-vm-01

# Start london-vm-02 Worker VM
virsh start london-vm-02