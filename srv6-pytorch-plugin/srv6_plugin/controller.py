"""
Network controller for SRv6 route programming.
"""

import os
import logging
import requests
from .route_programmer import RouteProgrammerFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NetworkProgrammer:
    """
    Network programmer that interfaces with the Jalapeño API to get
    optimal routes and programs them on the local system.
    """
    
    def __init__(self, api_endpoint: str):
        """
        Initialize with the network API endpoint.
        
        Args:
            api_endpoint: URL of the Jalapeño API endpoint.
        """
        self.api_endpoint = api_endpoint
        self.collection_name = os.environ.get('TOPOLOGY_COLLECTION', 'network_topology')
        
        # Initialize route programmer - default to Linux
        platform = os.environ.get('ROUTE_PLATFORM', 'linux')
        try:
            self.route_programmer = RouteProgrammerFactory.get_programmer(platform)
        except Exception as e:
            logger.error(f"Failed to initialize route programmer: {e}")
            logger.warning("Route programming will be disabled")
            self.route_programmer = None
    
    def get_route_info(self, source: str, destination: str) -> dict:
        """
        Get route information from the API.
        
        Args:
            source: Source node identifier (e.g., 'hosts/host01')
            destination: Destination node identifier (e.g., 'hosts/host02')
            
        Returns:
            API response dictionary or None if the call failed.
        """
        try:
            url = f"{self.api_endpoint}/graphs/{self.collection_name}/shortest_path/load"
            params = {
                'source': source,
                'destination': destination,
                'direction': 'outbound'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return data
        except Exception as e:
            logger.error(f"Network API call failed for {source} -> {destination}: {e}")
            return None
    
    def program_route(self, destination: str, srv6_data: dict, interface: str = 'eth1') -> bool:
        """
        Program an SRv6 route.
        
        Args:
            destination: Destination IP address or CIDR prefix.
            srv6_data: SRv6 data from the API response.
            interface: Outbound interface name.
            
        Returns:
            True if the route was programmed successfully.
        """
        if not self.route_programmer:
            logger.error("Route programmer not initialized, cannot program route")
            return False
        
        # Convert destination IP to CIDR if it's not already
        if '/' not in destination:
            # Use /128 for IPv6, /32 for IPv4
            prefix_len = "128" if ':' in destination else "32"
            destination = f"{destination}/{prefix_len}"
        
        try:
            logger.info(f"  Route to {destination}, SRv6 data: {srv6_data}")
            # Program the route
            success, message = self.route_programmer.program_route(
                destination_prefix=destination,
                srv6_usid=srv6_data['srv6_usid'],
                outbound_interface=interface,
                table_id=int(os.environ.get('ROUTE_TABLE_ID', '254'))
            )
            
            return success
        except Exception as e:
            logger.error(f"Exception during route programming: {e}")
            return False
    
    def program_all_routes(self, nodes: list) -> bool:
        """
        Program routes for all node pairs.
        
        Args:
            nodes: List of node info dictionaries from get_all_nodes().
            
        Returns:
            True if routes were programmed (even if some failed).
        """
        if not self.route_programmer:
            logger.error("Route programmer not initialized, cannot program routes")
            return False
        
        # Get current node's hostname
        rank = int(os.environ.get('RANK', '0'))
        current_host = None
        
        # Find the current node's hostname from the nodes list
        for node in nodes:
            if node['rank'] == rank:
                current_host = f"hosts/{node['hostname']}"
                break
        
        if not current_host:
            logger.error(f"Could not find hostname for rank {rank}")
            return False
        
        # Only generate routes from current host to other nodes
        all_pairs = []
        for node in nodes:
            if node['rank'] != rank:  # Skip self
                all_pairs.append({
                    'source': current_host,
                    'destination': f"hosts/{node['hostname']}"
                })
        
        # Program one route per destination
        for pair in all_pairs:
            api_response = self.get_route_info(pair['source'], pair['destination'])
            if api_response and api_response.get('found'):
                srv6_data = api_response.get('srv6_data', {})
                if srv6_data:
                    # Extract destination network from the API response
                    dest_info = api_response.get('destination_info', {})
                    if not dest_info or 'prefix' not in dest_info or 'prefix_len' not in dest_info:
                        logger.warning(f"No prefix information found for {pair['destination']}")
                        continue
                    
                    # Determine IP version from MASTER_ADDR
                    master_addr = os.environ.get('MASTER_ADDR', '')
                    is_ipv6 = ':' in master_addr
                    
                    # Use the appropriate prefix and prefix_len from the API response
                    if is_ipv6:
                        if not dest_info.get('ipv6_address'):
                            logger.warning(f"No IPv6 address found for {pair['destination']}")
                            continue
                        dest_ip = f"{dest_info['prefix']}/{dest_info['prefix_len']}"
                    else:
                        if not dest_info.get('ipv4_address'):
                            logger.warning(f"No IPv4 address found for {pair['destination']}")
                            continue
                        dest_ip = f"{dest_info['prefix']}/{dest_info['prefix_len']}"
                    
                    try:
                        self.program_route(
                            destination=dest_ip,
                            srv6_data=srv6_data,
                            interface=os.environ.get('BACKEND_INTERFACE', 'eth1')
                        )
                    except Exception as e:
                        logger.error(f"Error programming route to {pair['destination']}: {e}")
                else:
                    logger.warning(f"No SRv6 data found in API response for {pair['destination']}")
            else:
                logger.warning(f"No route found for {pair['source']} -> {pair['destination']}")
        
        return True

