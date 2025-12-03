#!/usr/bin/env python3

import json
import os
import argparse

def get_host_prefix(hostname):
    """
    Map hostname to its corresponding prefix
    Args:
        hostname: Hostname (e.g., 'host01')
    Returns:
        str: The corresponding prefix (e.g., '2001:db8:1001::/64')
    """
    # Extract the host number and ensure it's padded to 4 digits
    host_num = hostname.replace('host', '')
    return f"2001:db8:10{host_num}::/64"

def reverse_usid_segments(usid):
    """
    Reverse the path segments in a USID while keeping the uSID block at the start
    Args:
        usid: Original USID (e.g., 'fc00:0:1202:1000:1201::')
    Returns:
        str: USID with reversed path segments and fe06 appended (e.g., 'fc00:0:1201:1000:1202:fe06::')
    """
    # Split the USID into segments, excluding the trailing ::
    segments = usid.rstrip(':').split(':')
    
    # Keep the first two segments (uSID block) and reverse the rest (path segments)
    usid_block = segments[:2]  # ['fc00', '0']
    path_segments = segments[2:]  # ['1202', '1000', '1201']
    reversed_path = path_segments[::-1]  # ['1201', '1000', '1202']
    
    # Combine everything and append :fe06::
    return ':'.join(usid_block + reversed_path) + ':fe06::'

def generate_shell_script(paths_data):
    """
    Generate a shell script with SRv6 routes based on paths.json data
    Args:
        paths_data: List of path entries from paths.json
    """
    script_content = "#!/bin/bash\n\n"
    
    # Process each path
    for path in paths_data:
        # Extract source and destination host numbers
        src_host = path['source'].split('/')[-1]
        dst_host = path['destination'].split('/')[-1]
        
        # Get the USIDs (forward and reverse)
        forward_usid = path['srv6']['usid'].rstrip(':') + ':fe06::'
        reverse_usid = reverse_usid_segments(path['srv6']['usid'])
        
        # Get the correct prefixes
        dst_prefix = get_host_prefix(dst_host)
        src_prefix = get_host_prefix(src_host)
        
        # Generate forward path (source to destination)
        script_content += f"# Path {path['path']}\n"
        script_content += f"# {src_host} to {dst_host}\n"
        script_content += f"echo \"adding srv6 route for {src_host} to {dst_host}\"\n"
        script_content += f"docker exec -it clab-sonic-{src_host} ip -6 route add {dst_prefix} encap seg6 mode encap segs {forward_usid} dev eth1\n\n"
        
        # Generate reverse path (destination to source)
        script_content += f"# {dst_host} to {src_host}\n"
        script_content += f"echo \"adding srv6 route for {dst_host} to {src_host}\"\n"
        script_content += f"docker exec -it clab-sonic-{dst_host} ip -6 route add {src_prefix} encap seg6 mode encap segs {reverse_usid} dev eth1\n\n"
    
    return script_content

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate SRv6 route configuration script from paths.json')
    parser.add_argument('-i', '--input', default='paths.json',
                      help='Input paths.json file (default: paths.json)')
    parser.add_argument('-o', '--output', default='docker-exec.sh',
                      help='Output shell script file (default: docker-exec.sh)')
    args = parser.parse_args()
    
    try:
        # Read paths.json
        with open(args.input, 'r') as f:
            paths_data = json.load(f)
        
        # Generate shell script content
        script_content = generate_shell_script(paths_data)
        
        # Write to output file
        with open(args.output, 'w') as f:
            f.write(script_content)
        
        # Make the script executable
        os.chmod(args.output, 0o755)
        
        print(f"Generated {args.output} successfully!")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file '{args.input}'")
    except json.JSONDecodeError:
        print(f"Error: '{args.input}' is not a valid JSON file")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 