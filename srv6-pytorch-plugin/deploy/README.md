# Kubernetes Deployment

This directory contains example Kubernetes manifests for deploying the SRv6 PyTorch Plugin.

## Prerequisites

1. **Kubernetes cluster** with:
   - Cilium CNI (or another CNI supporting SRv6)
   - Multus CNI for secondary network interfaces
   - Access to the Jalapeño API

2. **Container image** built and available:
   ```bash
   # From the repo root
   docker build -t srv6-pytorch-plugin:latest .
   ```

3. **NetworkAttachmentDefinition** for the backend network:
   ```yaml
   apiVersion: k8s.cni.cncf.io/v1
   kind: NetworkAttachmentDefinition
   metadata:
     name: backend-network
   spec:
     config: '{
       "cniVersion": "0.3.1",
       "type": "macvlan",
       "master": "ens5",
       "mode": "bridge",
       "ipam": {
         "type": "static"
       }
     }'
   ```

## Environment Variables

The following environment variables must be configured in your pod spec:

| Variable | Description |
|----------|-------------|
| `RANK` | Pod's rank (0, 1, 2, ...) |
| `WORLD_SIZE` | Total number of training pods |
| `MASTER_ADDR` | IPv6 address of the rank-0 pod's backend interface |
| `MASTER_PORT` | Port for distributed training (default: 29500) |
| `BACKEND_INTERFACE` | Interface name from Multus (usually `net1`) |
| `JALAPENO_API_ENDPOINT` | Jalapeño API URL |
| `TOPOLOGY_COLLECTION` | ArangoDB graph collection name |
| `HOSTS` | Comma-separated list of all hosts/training pods |

## Example Pod Manifest

See the lab's `srv6-pytorch-training-test.yaml` for a complete example with:
- Multiple training pods with different ranks
- ConfigMap for shared configuration
- Multus network annotations for secondary interfaces
- Proper security context for route programming

