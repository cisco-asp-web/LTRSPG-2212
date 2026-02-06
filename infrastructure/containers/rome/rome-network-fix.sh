# --- Rome Configuration ---
# Copy and paste these commands into the Rome terminal

# 1. Bring up the interface
ip link set eth1 up
ip addr flush dev eth1

# 2. Assign IP Addresses
ip addr add 10.107.1.2/24 dev eth1
ip addr add fc00:0:107:1::2/64 dev eth1

# 3. Add Routes
ip route add 10.0.0.0/8 via 10.107.1.1 dev eth1
ip route add 10.1.1.0/24 via 10.107.1.1 dev eth1
ip route add 10.8.0.0/16 via 10.107.1.1 dev eth1
ip -6 route add fc00:0::/32 via fc00:0:107:1::1 dev eth1
ip -6 route add fc00:0:101:1::/64 via fc00:0:107:1::1 dev eth1
