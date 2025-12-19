# Containerlab Ubuntu Utility Node: London (.108) – Dockerfile + Entrypoint Overview

This document describes **the exact same utility container design** used across the lab, with only **site-specific variables** changing between nodes.

This file corresponds to the **London** utility node.

---

## Design intent (common to all sites)

This container is a **generic Ubuntu 22.04 utility host** used in the lab to:

- Provide SSH access instead of `docker exec`
- Act as a Linux troubleshooting endpoint
- Validate IPv4 and IPv6 connectivity
- Test routing, MTU, queues, DNS, and reachability
- Behave like a small “host behind the router”

All sites use:
- The **same Dockerfile**
- The **same entrypoint logic**
- The **same operational model**

Only **IP addresses, routes, and interface roles** differ.

---

# Dockerfile (common across all sites)

## Base image
```dockerfile
FROM ubuntu:22.04
```

Stable, predictable, and widely supported for labs.

---

## Non-interactive installs
```dockerfile
ENV DEBIAN_FRONTEND=noninteractive
```

Prevents `apt` prompts during build.

---

## Installed packages (identical for all nodes)
```dockerfile
RUN apt-get update && apt-get install -y \
    iproute2 iputils-ping curl net-tools \
    traceroute mtr-tiny tcpdump \
    openssh-server sudo vim ca-certificates procps \
    iperf3 socat dnsutils nmap fping jq \
    ndisc6 \
    python3 python3-pip \
  && rm -rf /var/lib/apt/lists/*
```

### Why this toolset exists
- **Core networking:** `ip`, `ping`, `curl`
- **Path analysis:** `traceroute`, `mtr`
- **Packet inspection:** `tcpdump`
- **Throughput & flow testing:** `iperf3`, `socat`
- **DNS & discovery:** `dig`, `ndisc6`
- **Scanning & probing:** `nmap`, `fping`
- **Automation support:** Python 3
- **Human convenience:** `vim`, `jq`, `sudo`

---

## SSH runtime setup
```dockerfile
RUN mkdir -p /var/run/sshd
```

Required by OpenSSH.

---

## Users (same everywhere)
```dockerfile
user: cisco
user: admin
```
- Password authentication enabled
- Passwordless sudo
- Intended for lab speed and workshops

---

## SSH behavior
- Password authentication: **enabled**
- Root login: **disabled**
- SSH runs as PID 1

---

## Entrypoint behavior
```dockerfile
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-D", "-e"]
```

The entrypoint:
1. Normalizes interfaces
2. Applies site-specific networking
3. Hands off to `sshd`

---

# entrypoint.sh (common logic)

## 1) Interface normalization
- MTU fixed to 1500
- txqueuelen set to 1000
- Applied to all `eth*` interfaces

Purpose:
- Avoid Containerlab/Docker edge cases
- Stable behavior during throughput tests

---

## 2) Management interface (eth0)

| Variable | Value |
|--------|------|
| IPv4 address | 172.20.6.108/24 |
| Gateway | 172.20.6.1 |
| Role | SSH / management |

Behavior:
- Only reconfigures eth0 if IP does not already match
- Ensures deterministic SSH access

---

## DNS behavior
```text
nameserver 8.8.8.8
```

Pinned for lab reliability.

---

## 3) Data-plane interface (eth1)

| Variable | Value |
|--------|------|
| IPv4 address | 10.101.1.2/24 |
| IPv6 address | fc00:0:101:1::2/64 |
| Gateway | 10.101.1.1 |

Routes:
- Lab prefixes routed via site gateway
- IPv4 + IPv6 enabled

---

## 4) Optional interface (eth2)

- Brought up if present
- No fixed addressing
- Future-proofing for topology evolution

---

## 5) Process handover

- `sshd` replaces the shell
- Container remains alive
- Logs visible via `docker logs`

---

# Operational notes (identical everywhere)

## Validation checklist
```bash
ip addr
ip route
ip -6 route
ss -lntp | grep :22
```

## Connectivity tests
```bash
ping -c 2 172.20.6.1
ping -c 2 10.101.1.1
ping6 -c 2 fc00:0:101:1::1
```

---

# Security disclaimer

This container is **intentionally relaxed**:
- Password SSH
- Passwordless sudo

It is suitable **only for isolated lab environments**.

---

# Build the container Image:

```
docker build -t cl-london-container:latest:latest .
```

# Summary

This node is one instance of a **standardized lab utility container**.

- Dockerfile: identical everywhere
- Entrypoint logic: identical everywhere
- Differences are **purely variables**
  - IPs
  - Routes
  - Site naming

This ensures:
- Predictability
- Reproducibility
- Low cognitive load during labs
