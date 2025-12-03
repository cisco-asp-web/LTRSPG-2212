import os
import logging
from dist_setup import init_distributed, get_all_nodes
from controller import NetworkProgrammer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemoPlugin:
    """Simple wrapper for the demo that combines distributed setup and network programming"""
    
    def __init__(self, api_endpoint):
        """Initialize with the network API endpoint"""
        self.api_endpoint = api_endpoint
        self.network_programmer = NetworkProgrammer(api_endpoint)
    
    def init_process_group(self, backend='gloo', **kwargs):
        """Initialize distributed training and program routes"""
        #logger.info("Initializing distributed training...")
        # First, initialize PyTorch distributed
        if not init_distributed():
            logger.error("Failed to initialize distributed training")
            return False
        
        try:
            # Get information about all nodes
            logger.info(" Getting node information...")
            nodes = get_all_nodes()
            
            # Program routes
            #logger.info("  Begin programming routes...")
            self.network_programmer.program_all_routes(nodes)
            
            logger.info(" Initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            return False 