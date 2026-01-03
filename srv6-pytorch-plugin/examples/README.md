# SRv6 PyTorch Plugin Examples

This directory contains example scripts demonstrating how to use the SRv6 PyTorch Plugin.

## test_connectivity.py

A comprehensive test that:
1. Initializes PyTorch distributed training across multiple nodes
2. Queries the Jalapeño API for optimal SRv6 paths
3. Programs SRv6 routes on each node
4. Tests connectivity between all nodes using ping

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RANK` | Yes | `0` | This node's rank in the distributed training |
| `WORLD_SIZE` | Yes | `2` | Total number of nodes |
| `MASTER_ADDR` | Yes | - | IP address of the master node |
| `MASTER_PORT` | No | `29500` | Port for distributed training communication |
| `BACKEND_INTERFACE` | No | `net1` | Network interface for backend traffic |
| `JALAPENO_API_ENDPOINT` | Yes | - | URL of the Jalapeño API |
| `TOPOLOGY_COLLECTION` | No | `network_topology` | ArangoDB graph collection name |
| `HOSTS` | Yes | - | Comma-separated list of participating hosts/training pods |
| `HOSTNAME` | No | Auto | Override this node's hostname |

### Running Locally

```bash
# Create a .env file with your configuration
cat > .env << EOF
RANK=0
WORLD_SIZE=2
MASTER_ADDR=fcbb:0:0800:0::10
MASTER_PORT=29500
BACKEND_INTERFACE=net1
JALAPENO_API_ENDPOINT=http://jalapeno-api:8080
TOPOLOGY_COLLECTION=network_topology
HOSTS=host01,host02
EOF

# Run the test
python test_connectivity.py
```

### Running in Kubernetes

See the `deploy/` directory for Kubernetes manifests that run this test across multiple pods.

