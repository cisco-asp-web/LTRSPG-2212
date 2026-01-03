# SRv6 PyTorch Plugin

A PyTorch distributed training plugin that leverages SRv6 (Segment Routing over IPv6) for intelligent traffic engineering. The plugin integrates with [Jalapeño](https://github.com/cisco-open/jalapeno) to dynamically program optimal network paths between distributed training nodes.

## Features

- **Automatic SRv6 Route Programming**: Queries the Jalapeño API for optimal paths and programs SRv6 encapsulation routes
- **PyTorch Distributed Integration**: Seamlessly integrates with `torch.distributed` for distributed training
- **Multi-Platform Support**: Route programming for Linux (via pyroute2) and VPP
- **IPv4/IPv6 Support**: Works with both IPv4 and IPv6 networks
- **Kubernetes Ready**: Designed for containerized deployments with Multus CNI support

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Distributed Training Job                     │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│   Node 0    │   Node 1    │   Node 2    │   Node 3    │   ...   │
│ ┌─────────┐ │ ┌─────────┐ │ ┌─────────┐ │ ┌─────────┐ │         │
│ │ PyTorch │ │ │ PyTorch │ │ │ PyTorch │ │ │ PyTorch │ │         │
│ │ Process │ │ │ Process │ │ │ Process │ │ │ Process │ │         │
│ └────┬────┘ │ └────┬────┘ │ └────┬────┘ │ └────┬────┘ │         │
│      │      │      │      │      │      │      │      │         │
│ ┌────▼────┐ │ ┌────▼────┐ │ ┌────▼────┐ │ ┌────▼────┐ │         │
│ │  SRv6   │ │ │  SRv6   │ │ │  SRv6   │ │ │  SRv6   │ │         │
│ │ Plugin  │ │ │ Plugin  │ │ │ Plugin  │ │ │ Plugin  │ │         │
│ └────┬────┘ │ └────┬────┘ │ └────┬────┘ │ └────┬────┘ │         │
└──────┼──────┴──────┼──────┴──────┼──────┴──────┼──────┴─────────┘
       │             │             │             │
       └─────────────┴──────┬──────┴─────────────┘
                            │
                     ┌──────▼──────┐
                     │  Jalapeño   │
                     │     API     │
                     └─────────────┘
```

## Installation

### From Source

```bash
git clone https://github.com/your-org/srv6-pytorch-plugin.git
cd srv6-pytorch-plugin
pip install -e .
```

### Using pip (from source)

```bash
# Clone and install locally
git clone https://github.com/segmentrouting/srv6-pytorch-plugin.git
cd srv6-pytorch-plugin
pip install .
```

### Docker

```bash
docker build -t srv6-pytorch-plugin:latest .
```

## Quick Start

```python
from srv6_plugin import SRv6Plugin

# Initialize the plugin with your Jalapeño API endpoint
plugin = SRv6Plugin("http://jalapeno-api:8080")

# Initialize distributed training and program SRv6 routes
if plugin.init_process_group():
    # Your distributed training code here
    pass
```

## Configuration

The plugin is configured via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RANK` | Yes | `0` | This node's rank in the distributed training |
| `WORLD_SIZE` | Yes | `2` | Total number of nodes |
| `MASTER_ADDR` | Yes | - | IP address of the master node |
| `MASTER_PORT` | No | `29500` | Port for distributed training |
| `BACKEND_INTERFACE` | No | `net1` | Network interface for SRv6 traffic |
| `JALAPENO_API_ENDPOINT` | Yes | - | Jalapeño API URL |
| `TOPOLOGY_COLLECTION` | No | `network_topology` | ArangoDB graph collection |
| `ROUTE_PLATFORM` | No | `linux` | Route programmer: `linux` or `vpp` |
| `ROUTE_TABLE_ID` | No | `254` | Linux routing table ID |
| `SRV6_ENCAP_MODE` | No | `encap.red` | SRv6 encap mode: `encap` or `encap.red` |

## Requirements

- Python 3.10+
- PyTorch 2.0+ (CPU or GPU version)
- Root/CAP_NET_ADMIN for route programming
- Access to a Jalapeño API instance

## Project Structure

```
srv6-pytorch-plugin/
├── srv6_plugin/           # Core plugin package
│   ├── __init__.py
│   ├── plugin.py          # Main SRv6Plugin class
│   ├── distributed.py     # PyTorch distributed utilities
│   ├── controller.py      # Network programming controller
│   └── route_programmer.py # Linux/VPP route programmers
├── examples/              # Example scripts
│   └── test_connectivity.py
├── deploy/                # Kubernetes deployment examples
├── Dockerfile
├── requirements.txt
└── pyproject.toml
```

## Kubernetes Deployment

See the `deploy/` directory for Kubernetes manifests. The plugin works with:

- **Cilium** as the primary CNI
- **Multus** for secondary network interfaces
- **macvlan** for backend SRv6 traffic

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## Related Projects

- [Jalapeño](https://github.com/cisco-open/jalapeno) - Network topology and path computation
- [PyTorch Distributed](https://pytorch.org/docs/stable/distributed.html) - Distributed training framework
- [Cilium](https://cilium.io/) - eBPF-based networking

