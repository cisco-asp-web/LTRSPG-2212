"""
Main SRv6 Plugin class for PyTorch distributed training.
"""

import os
import logging
from .distributed import init_distributed, get_all_nodes
from .controller import NetworkProgrammer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SRv6Plugin:
    """
    SRv6 Plugin for PyTorch distributed training.
    
    Combines distributed setup and network programming to enable
    SRv6-based traffic engineering for ML workloads.
    
    Example:
        >>> plugin = SRv6Plugin("http://api-endpoint:8080")
        >>> if plugin.init_process_group():
        ...     # Training code here
        ...     pass
    """
    
    def __init__(self, api_endpoint: str):
        """
        Initialize with the network API endpoint.
        
        Args:
            api_endpoint: URL of the Jalapeño API endpoint for route lookups.
        """
        self.api_endpoint = api_endpoint
        self.network_programmer = NetworkProgrammer(api_endpoint)
    
    def init_process_group(self, backend: str = 'gloo', **kwargs) -> bool:
        """
        Initialize distributed training and program SRv6 routes.
        
        This method:
        1. Initializes PyTorch distributed process group
        2. Gathers information about all nodes in the training job
        3. Programs SRv6 routes between nodes for optimized communication
        
        Args:
            backend: PyTorch distributed backend ('gloo' for CPU, 'nccl' for GPU).
            **kwargs: Additional arguments passed to dist.init_process_group.
            
        Returns:
            True if initialization succeeded, False otherwise.
        """
        # First, initialize PyTorch distributed
        if not init_distributed():
            logger.error("Failed to initialize distributed training")
            return False
        
        try:
            # Get information about all nodes
            logger.info(" Getting node information...")
            nodes = get_all_nodes()
            
            # Program routes
            self.network_programmer.program_all_routes(nodes)
            
            logger.info(" Initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            return False


# Backward compatibility alias
DemoPlugin = SRv6Plugin

