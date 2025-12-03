#!/bin/bash

# Path 1
# host01 to host03
echo "adding srv6 route for host01 to host03"
docker exec -it clab-sonic-host01 ip -6 route add 2001:db8:1003::/64 encap seg6 mode encap segs fc00:0:1201:1000:1203:fe06:: dev eth1

# host03 to host01
echo "adding srv6 route for host03 to host01"
docker exec -it clab-sonic-host03 ip -6 route add 2001:db8:1001::/64 encap seg6 mode encap segs fc00:0:1203:1000:1201:fe06:: dev eth1

# Path 2
# host01 to host00
echo "adding srv6 route for host01 to host00"
docker exec -it clab-sonic-host01 ip -6 route add 2001:db8:1000::/64 encap seg6 mode encap segs fc00:0:1201:1001:1200:fe06:: dev eth1

# host00 to host01
echo "adding srv6 route for host00 to host01"
docker exec -it clab-sonic-host00 ip -6 route add 2001:db8:1001::/64 encap seg6 mode encap segs fc00:0:1200:1001:1201:fe06:: dev eth1

# Path 3
# host03 to host00
echo "adding srv6 route for host03 to host00"
docker exec -it clab-sonic-host03 ip -6 route add 2001:db8:1000::/64 encap seg6 mode encap segs fc00:0:1203:1000:1200:fe06:: dev eth1

# host00 to host03
echo "adding srv6 route for host00 to host03"
docker exec -it clab-sonic-host00 ip -6 route add 2001:db8:1003::/64 encap seg6 mode encap segs fc00:0:1200:1000:1203:fe06:: dev eth1
