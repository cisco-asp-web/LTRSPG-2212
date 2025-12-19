#!/bin/sh
set -eu

log() { echo "[netcfg] $*"; }

# ---- helpers ----
link_up() {
  IF="$1"
  if ip link show "$IF" >/dev/null 2>&1; then
    ip link set "$IF" up || true
  else
    log "WARN: interface $IF not found (skipping)"
    return 1
  fi
  return 0
}

addr4_replace() { ip addr replace "$1" dev "$2"; }
addr6_replace() { ip -6 addr replace "$1" dev "$2"; }

route4_replace() { ip route replace "$1" via "$2" dev "$3"; }
route6_replace() { ip -6 route replace "$1" via "$2" dev "$3"; }

# ---- enable IPv6 (best-effort) ----
# Some container environments ignore these; harmless if they fail.
sysctl -w net.ipv6.conf.all.disable_ipv6=0 >/dev/null 2>&1 || true
sysctl -w net.ipv6.conf.default.disable_ipv6=0 >/dev/null 2>&1 || true

# ---- bring up loopback + interfaces (best-effort) ----
link_up lo || true
HAVE_ETH0=0; HAVE_ETH1=0; HAVE_ETH2=0
link_up eth0 && HAVE_ETH0=1 || true
link_up eth1 && HAVE_ETH1=1 || true
link_up eth2 && HAVE_ETH2=1 || true

# ---- eth0: mgmt + default gw + DNS ----
if [ "$HAVE_ETH0" -eq 1 ]; then
  log "Configuring eth0"
  addr4_replace 172.20.6.109/24 eth0

  # default IPv4 gateway on eth0
  ip route replace default via 172.20.6.1 dev eth0

  # DNS (best-effort; Docker may manage resolv.conf)
  if [ -w /etc/resolv.conf ]; then
    grep -q '^nameserver 8.8.8.8' /etc/resolv.conf 2>/dev/null \
      || printf "nameserver 8.8.8.8\n" > /etc/resolv.conf
  else
    log "WARN: /etc/resolv.conf not writable (skipping DNS set)"
  fi
fi

# ---- eth1: IPv4/IPv6 + routes ----
if [ "$HAVE_ETH1" -eq 1 ]; then
  log "Configuring eth1"
  addr4_replace 10.107.1.2/24 eth1
  addr6_replace fc00:0:107:1::2/64 eth1

  # IPv4 routes via 10.107.1.1
  route4_replace 10.0.0.0/24     10.107.1.1 eth1
  route4_replace 10.1.1.0/24     10.107.1.1 eth1
  route4_replace 10.101.1.0/24   10.107.1.1 eth1
  route4_replace 10.8.0.0/24     10.107.1.1 eth1

  # IPv6 route via fc00:0:107:1::1
  route6_replace fc00:0::/32     fc00:0:107:1::1 eth1
fi

# ---- eth2: IPv4/IPv6 + routes ----
if [ "$HAVE_ETH2" -eq 1 ]; then
  log "Configuring eth2"
  addr4_replace 10.107.2.2/24 eth2
  addr6_replace fc00:0:107:2::2/64 eth2

  # IPv4 routes via 10.107.2.1
  route4_replace 10.101.2.0/24   10.107.2.1 eth2
  route4_replace 10.200.0.0/24   10.107.2.1 eth2

  # IPv6 route via fc00:0:107:2::1
  route6_replace fc00:0:101:2::/64 fc00:0:107:2::1 eth2
fi

# ---- loopback VIPs ----
log "Configuring loopback addresses"
addr4_replace 20.0.0.1/24 lo
addr4_replace 30.0.0.1/24 lo
addr4_replace 40.0.0.1/24 lo
addr4_replace 50.0.0.1/24 lo
addr6_replace fc00:0:40::1/64 lo
addr6_replace fc00:0:50::1/64 lo

# ---- show resulting config (useful in logs) ----
log "Final interface state:"
ip -br a || true
log "IPv4 routes:"
ip r || true
log "IPv6 routes:"
ip -6 r || true