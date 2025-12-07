import os
import logging
import torch.distributed as dist
import netifaces

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_node_info(backend_iface='eth1'):
    """Get node information including hostname and IP address"""
    # Get hostname from environment variable, with a default based on rank
    hostname = os.environ.get('HOSTNAME')
    if not hostname:
        hostname_prefix = os.environ.get('HOSTNAME_PREFIX', 'host')
        hostname = f"{hostname_prefix}{int(os.environ.get('RANK', '0')):02d}"
    
    # Get IPv6 address from the backend interface
    addrs = netifaces.ifaddresses(backend_iface)
    local_ip = None
    if netifaces.AF_INET6 in addrs:
        for addr in addrs[netifaces.AF_INET6]:
            if 'addr' in addr and not addr['addr'].startswith('fe80::'):  # Skip link-local addresses
                local_ip = addr['addr']
                break
    
    if not local_ip:
        raise ValueError(f"Could not determine IPv6 address for interface {backend_iface}")
    
    return {
        'hostname': hostname,
        'ip_address': local_ip,
        'rank': int(os.environ.get('RANK', '0'))
    }

def init_distributed():
    """Initialize PyTorch distributed training"""
    # Get distributed training info
    rank = int(os.environ.get('RANK', '0'))
    world_size = int(os.environ.get('WORLD_SIZE', '1'))
    master_addr = os.environ.get('MASTER_ADDR', 'localhost')
    master_port = os.environ.get('MASTER_PORT', '29500')
    
    logger.info(f"  Initializing distributed training:")
    logger.info(f"  Rank: {rank}")
    logger.info(f"  World Size: {world_size}")
    logger.info(f"  Master Address: {master_addr}")
    logger.info(f"  Master Port: {master_port}")
    
    # Format the init_method URL based on whether master_addr is IPv6
    if ':' in master_addr:  # IPv6 address
        init_method = f"tcp://[{master_addr}]:{master_port}"
    else:  # IPv4 address
        init_method = f"tcp://{master_addr}:{master_port}"
    
    logger.info(f"  Using init_method: {init_method}")
    
    # Initialize the process group
    logger.info("  Initializing PyTorch distributed process group...")
    try:
        dist.init_process_group(
            backend='gloo',  # Use gloo backend for CPU
            init_method=init_method,
            world_size=world_size,
            rank=rank
        )
        #logger.info("dist.init_process_group completed successfully")
        
        # Verify initialization
        if dist.is_initialized():
            return True
        else:
            logger.error("PyTorch distributed initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"Failed to initialize PyTorch distributed: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e)}")
        return False

def get_all_nodes():
    """Get information about all nodes in the distributed setup"""
    if not dist.is_initialized():
        raise RuntimeError("Distributed training not initialized")
    
    rank = dist.get_rank()
    world_size = dist.get_world_size()
    
    # Get local node info
    local_info = get_node_info()
    
    # Convert node info to tensor for all_gather
    import torch
    import json
    
    node_info_tensor = torch.tensor(bytearray(json.dumps(local_info).encode()))
    node_info_size = torch.tensor([len(node_info_tensor)])
    
    # Gather sizes from all ranks
    size_list = [torch.zeros_like(node_info_size) for _ in range(world_size)]
    dist.all_gather(size_list, node_info_size)
    
    # Calculate max size and pad tensors
    max_size = max(size.item() for size in size_list)
    padded_tensor = torch.zeros(max_size, dtype=torch.uint8)
    padded_tensor[:len(node_info_tensor)] = node_info_tensor
    
    # Gather all node information
    gathered_tensors = [torch.zeros_like(padded_tensor) for _ in range(world_size)]
    dist.all_gather(gathered_tensors, padded_tensor)
    
    # Convert gathered tensors back to node info
    all_nodes = []
    for tensor, size in zip(gathered_tensors, size_list):
        node_info_bytes = tensor[:size.item()].tolist()
        node_info_str = bytes(node_info_bytes).decode()
        all_nodes.append(json.loads(node_info_str))
    
    # Sort nodes by rank to ensure consistent order
    all_nodes.sort(key=lambda x: x['rank'])
    return all_nodes 