# Multus CNI Setup Guide

This guide explains how to install and configure Multus CNI to provide a secondary backend network interface for PyTorch pods in your Kubernetes cluster.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Node                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                         Pod                                │  │
│  │   ┌─────────┐                          ┌─────────┐        │  │
│  │   │  eth0   │  Primary (Cilium)        │  net1   │ Backend│  │
│  │   └────┬────┘                          └────┬────┘        │  │
│  └────────┼─────────────────────────────────────┼────────────┘  │
│           │                                     │               │
│  ┌────────▼────────┐                  ┌─────────▼────────┐     │
│  │   Cilium CNI    │                  │  IPVLAN/MACVLAN  │     │
│  │  (via Multus)   │                  │   (via Multus)   │     │
│  └────────┬────────┘                  └─────────┬────────┘     │
│           │                                     │               │
│  ┌────────▼────────┐                  ┌─────────▼────────┐     │
│  │      ens4       │                  │       ens5       │     │
│  │  Frontend NIC   │                  │   Backend NIC    │     │
│  │  10.8.x.2/24    │                  │ fcbb:0:0800:x::/64│    │
│  └─────────────────┘                  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Kubernetes cluster initialized with kubeadm
- Cilium CNI installed and working
- Backend NIC (ens5) configured on all nodes

## Installation Steps

### Step 1: Install Multus CNI

Multus acts as a "meta-plugin" that wraps your primary CNI (Cilium) and enables additional network attachments.

```bash
kubectl apply -f multus-install.yaml
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

### Step 2: Install Whereabouts IPAM (Recommended)

Whereabouts provides cluster-wide IP address management for secondary networks. This prevents IP conflicts when pods are scheduled across different nodes.

```bash
kubectl apply -f whereabouts-install.yaml
```

Verify Whereabouts is running:
```bash
kubectl get pods -n kube-system -l app=whereabouts
```

### Step 3: Create NetworkAttachmentDefinition

The NetworkAttachmentDefinition (NAD) tells Multus how to configure the secondary network interface.

```bash
kubectl apply -f backend-network-nad.yaml
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

### Step 4: Deploy a Test Pod

```bash
kubectl apply -f pytorch-pod-example.yaml
```

Check the pod has both network interfaces:
```bash
kubectl exec pytorch-training -- ip addr
```

You should see:
- `eth0` - Primary interface via Cilium (172.16.x.x)
- `net1` - Backend interface via Multus (fcbb:0:0800:ffff::x)

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

### Check pod network status
```bash
kubectl get pod pytorch-training -o jsonpath='{.metadata.annotations.k8s\.v1\.cni\.cncf\.io/network-status}' | jq
```

### Test connectivity between pods on backend network
```bash
# From pytorch-worker-0
kubectl exec pytorch-worker-0 -- ping6 -c 3 <pytorch-worker-1-backend-ip>
```

## Troubleshooting

### Pod stuck in ContainerCreating

Check Multus logs:
```bash
kubectl logs -n kube-system -l app=multus --tail=50
```

Common issues:
- CNI binary not found: Verify `/opt/cni/bin/` contains ipvlan/macvlan binaries
- Interface not found: Verify ens5 exists on the node
- IPAM failure: Check whereabouts logs

### No secondary interface in pod

Verify the annotation is correct:
```bash
kubectl get pod <pod-name> -o yaml | grep -A5 annotations
```

### IP address conflicts

Switch from host-local to whereabouts IPAM, or ensure each node has a unique IP range.

## Files in this Directory

| File | Description |
|------|-------------|
| `multus-install.yaml` | Multus CNI DaemonSet and RBAC |
| `whereabouts-install.yaml` | Whereabouts IPAM DaemonSet and CRDs |
| `backend-network-nad.yaml` | NetworkAttachmentDefinition for ens5 |
| `pytorch-pod-example.yaml` | Example pods using the backend network |
| `multus-guide.md` | This guide |

## References

- [Multus CNI GitHub](https://github.com/k8snetworkplumbingwg/multus-cni)
- [Whereabouts IPAM](https://github.com/k8snetworkplumbingwg/whereabouts)
- [CNI Plugins](https://www.cni.dev/plugins/current/)

