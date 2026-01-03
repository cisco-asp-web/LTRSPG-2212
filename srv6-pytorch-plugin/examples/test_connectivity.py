#!/usr/bin/env python3
"""
SRv6 Connectivity Test Example

This script demonstrates how to use the SRv6 PyTorch Plugin to:
1. Initialize PyTorch distributed training
2. Program SRv6 routes via the Jalapeño API
3. Test connectivity between distributed training nodes

Usage:
    # Set required environment variables (or use a .env file)
    export RANK=0
    export WORLD_SIZE=2
    export MASTER_ADDR=fcbb:0:0800:0::10
    export MASTER_PORT=29500
    export BACKEND_INTERFACE=net1
    export JALAPENO_API_ENDPOINT=http://api:8080
    export TOPOLOGY_COLLECTION=network_topology
    export HOSTS=host01,host02
    
    # Run the test
    python test_connectivity.py
"""

import os
import time
import atexit
import torch.distributed as dist
from dotenv import load_dotenv

# Import from the srv6_plugin package
from srv6_plugin import SRv6Plugin

# Load environment variables from .env file (only if not already set)
# In Kubernetes, env vars are set by the pod spec/ConfigMap
load_dotenv(override=False)


def cleanup():
    """Cleanup function to destroy distributed process group."""
    if dist.is_initialized():
        dist.destroy_process_group()


# Register cleanup function
atexit.register(cleanup)


def get_all_nodes():
    """Get list of all nodes in the distributed setup from environment variables."""
    hosts = os.environ.get('HOSTS', '').split(',')
    nodes = []
    for i, hostname in enumerate(hosts):
        if hostname:  # Skip empty strings
            nodes.append({
                'rank': i,
                'hostname': hostname.strip()  # Remove any whitespace
            })
    return nodes


def main():
    # All configuration comes from environment variables
    # These should be set by the Kubernetes pod spec or .env file
    rank = int(os.getenv('RANK', '0'))
    world_size = int(os.getenv('WORLD_SIZE', '2'))
    master_addr = os.getenv('MASTER_ADDR')
    master_port = os.getenv('MASTER_PORT', '29500')
    backend_interface = os.getenv('BACKEND_INTERFACE', 'net1')
    
    # Validate required environment variables
    if not master_addr:
        print("Error: MASTER_ADDR environment variable is required")
        return
    
    # Set environment variables for torch.distributed
    os.environ['RANK'] = str(rank)
    os.environ['WORLD_SIZE'] = str(world_size)
    os.environ['MASTER_ADDR'] = master_addr
    os.environ['MASTER_PORT'] = master_port
    os.environ['BACKEND_INTERFACE'] = backend_interface
    
    try:
        # Initialize the plugin
        api_endpoint = os.getenv('JALAPENO_API_ENDPOINT')
        if not api_endpoint:
            print("Error: JALAPENO_API_ENDPOINT environment variable not set")
            return
        
        plugin = SRv6Plugin(api_endpoint)
        
        # Initialize distributed training
        if not plugin.init_process_group():
            print("Failed to initialize distributed training")
            return
            
        # Get nodes for connectivity test
        nodes = get_all_nodes()
            
        # Test connectivity
        # Get current node's hostname
        current_host = os.environ.get('HOSTNAME', f"host{rank:02d}")
        
        # Determine IP version from MASTER_ADDR
        master_addr = os.environ.get('MASTER_ADDR', '')
        is_ipv6 = ':' in master_addr
        
        # Test connectivity to all other nodes
        ping_success = 0
        ping_fail = 0
        
        for node in nodes:
            if node['hostname'] != current_host:  # Skip self
                print(f"\nTesting connectivity from {current_host} to {node['hostname']}...", flush=True)
                # Get the IP address from the API response
                api_response = plugin.network_programmer.get_route_info(
                    f"hosts/{current_host}",
                    f"hosts/{node['hostname']}"
                )
                if api_response and 'destination_info' in api_response:
                    dest_info = api_response['destination_info']
                    if is_ipv6:
                        ping_destination = dest_info.get('ipv6_address')
                    else:
                        ping_destination = dest_info.get('ipv4_address')
                        
                    if ping_destination:
                        print(f"Pinging {ping_destination}", flush=True)
                        ping_cmd = "ping6" if is_ipv6 else "ping"
                        result = os.system(f"{ping_cmd} -c 4 {ping_destination}")
                        if result == 0:
                            ping_success += 1
                        else:
                            ping_fail += 1
                    else:
                        print(f"Could not determine ping destination for {node['hostname']}", flush=True)
                        ping_fail += 1
                else:
                    print(f"Could not get route information for {node['hostname']}", flush=True)
                    ping_fail += 1
        
        # Report results
        if ping_fail == 0 and ping_success > 0:
            print(f"\nSRv6 connectivity test PASSED! ({ping_success} successful pings)", flush=True)
        elif ping_success > 0:
            print(f"\nSRv6 connectivity test PARTIAL: {ping_success} passed, {ping_fail} failed", flush=True)
        else:
            print(f"\nSRv6 connectivity test FAILED! ({ping_fail} failed attempts)", flush=True)
        
    except Exception as e:
        print(f"\nError during test: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Ensure all required environment variables are set")
        print("2. Check API endpoint connectivity")
        print("3. Verify interface name is correct")
        print("4. Check containerlab network connectivity")
        print("5. Verify all nodes can reach the master IP address")
        print("6. Check if the master port is available and not blocked")
    finally:
        # Ensure cleanup happens even if there's an error
        cleanup()


if __name__ == "__main__":
    main()

