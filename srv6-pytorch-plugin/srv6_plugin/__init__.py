"""
SRv6 PyTorch Plugin - SRv6 route programming for distributed PyTorch training.

This plugin enables PyTorch distributed training workloads to leverage
SRv6-enabled networks for optimized traffic engineering.
"""

from .plugin import SRv6Plugin
from .distributed import init_distributed, get_all_nodes, get_node_info
from .controller import NetworkProgrammer
from .route_programmer import (
    RouteProgrammer,
    LinuxRouteProgrammer,
    VPPRouteProgrammer,
    RouteProgrammerFactory
)

__version__ = "0.1.0"
__all__ = [
    "SRv6Plugin",
    "init_distributed",
    "get_all_nodes",
    "get_node_info",
    "NetworkProgrammer",
    "RouteProgrammer",
    "LinuxRouteProgrammer",
    "VPPRouteProgrammer",
    "RouteProgrammerFactory",
]

