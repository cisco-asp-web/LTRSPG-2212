# Multus CNI Setup Guide

This guide explains how to install and configure Multus CNI to provide a secondary backend network interface for PyTorch pods in your Kubernetes cluster.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Node                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                         Pod                               │  │
│  │   ┌─────────┐                          ┌─────────┐        │  │
│  │   │  eth0   │  Primary (Cilium)        │  net1   │ Backend│  │
│  │   └────┬────┘                          └────┬────┘        │  │
│  └────────┼─────────────────────────────────────┼────────────┘  │
│           │                                     │               │
│  ┌────────▼────────┐                  ┌─────────▼────────┐      │
│  │   Cilium CNI    │                  │  IPVLAN/MACVLAN  │      │
│  │  (via Multus)   │                  │   (via Multus)   │      │
│  └────────┬────────┘                  └─────────┬────────┘      │
│           │                                     │               │
│  ┌────────▼────────┐                  ┌─────────▼────────┐      │
│  │      ens4       │                  │       ens5       │      │
│  │  Frontend NIC   │                  │   Backend NIC    │      │
│  │  10.8.x.2/24    │                  │fcbb:0:0800:x::/64│      │
│  └─────────────────┘                  └──────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Kubernetes cluster initialized with kubeadm
- Cilium CNI installed and working
- Backend NIC (ens5) configured on all nodes

## Installation Steps

### Step 1: Install Multus CNI

Multus acts as a "meta-plugin" that wraps your primary CNI (Cilium) and enables additional network attachments.

#### Quickstart guide
https://github.com/k8snetworkplumbingwg/multus-cni/blob/master/docs/quickstart.md


```bash
kubectl apply -f multus-daemonset.yml
```

Verify Multus is running:
```bash
kubectl get pods -n kube-system -l app=multus
```

Expected output:
```
NAME                  READY   STATUS    RESTARTS   AGE
kube-multus-ds-xxxxx  1/1     Running   0          1m
kube-multus-ds-yyyyy  1/1     Running   0          1m
```

### Step 3: Create NetworkAttachmentDefinition

The NetworkAttachmentDefinition (NAD) tells Multus how to configure the secondary network interface.

```bash
kubectl apply -f multus-backend-network-nad.yaml
```

Verify the NAD was created:
```bash
kubectl get network-attachment-definitions
```

Expected output:
```
NAME               AGE
backend-network    5s
```

#### other NAD verifications
```bash
# List all NADs
kubectl get net-attach-def  # short form

# Describe a specific NAD to see the full config
kubectl describe net-attach-def backend-network

# View the raw YAML/JSON
kubectl get net-attach-def backend-network -o yaml
```

### Deploy a lightweight test pod
```bash
# Quick test with a minimal image instead
kubectl run multus-test --image=busybox --restart=Never \
  --overrides='{"metadata":{"annotations":{"k8s.v1.cni.cncf.io/networks":"backend-network-static"}}}' \
  -- sleep 600
```
or

```bash
kubectl apply -f multus-test.yaml
```

```bash
kubectl get pods -o wide
```

```bash
# Check interfaces and routes
kubectl exec multus-test-00 -- ip addr
kubectl exec multus-test-00 -- ip -6 route
kubectl exec multus-test-01 -- ip addr
kubectl exec multus-test-01 -- ip -6 route
kubectl exec multus-test-02 -- ip addr
kubectl exec multus-test-02 -- ip -6 route
```

```bash
# Clean up
kubectl delete pod multus-test
```

## Network Attachment Definition Options

### Option 1: IPVLAN (Recommended for VMs)

IPVLAN works well in virtualized environments because it doesn't require promiscuous mode.

```yaml
spec:
  config: |
    {
      "type": "ipvlan",
      "master": "ens5",
      "mode": "l3",
      "ipam": { ... }
    }
```

Modes:
- `l2` - Layer 2 mode (switch-like behavior)
- `l3` - Layer 3 mode (router-like behavior, recommended for IPv6)
- `l3s` - Layer 3 with source address validation

### Option 2: MACVLAN

MACVLAN assigns a unique MAC address to each pod. Requires promiscuous mode on the host.

```yaml
spec:
  config: |
    {
      "type": "macvlan",
      "master": "ens5",
      "mode": "bridge",
      "ipam": { ... }
    }
```

Enable promiscuous mode on each node (if using MACVLAN):
```bash
sudo ip link set ens5 promisc on
```

### Option 3: Bridge (for complex scenarios)

Creates a Linux bridge for more flexible networking.

## IPAM Options

### Whereabouts (Cluster-wide IPAM)

```json
"ipam": {
  "type": "whereabouts",
  "range": "fcbb:0:0800:ffff::/64",
  "enable_ipv6": true
}
```

### Host-local (Per-node IPAM)

```json
"ipam": {
  "type": "host-local",
  "ranges": [[{"subnet": "fcbb:0:0800:ffff::/64"}]]
}
```

⚠️ Warning: host-local can cause IP conflicts if pods on different nodes get the same IP.

### Static IP Assignment

Request specific IPs in the pod annotation:
```yaml
annotations:
  k8s.v1.cni.cncf.io/networks: |
    [{"name": "backend-network", "ips": ["fcbb:0:0800:ffff::50"]}]
```

## Verifying the Setup

### Check Multus logs
```bash
kubectl logs -n kube-system -l app=multus
```

## References

- [Multus CNI GitHub](https://github.com/k8snetworkplumbingwg/multus-cni)


