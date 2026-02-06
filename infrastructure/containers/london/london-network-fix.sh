# --- London Configuration ---
# Copy and paste these commands into the London terminal

# 1. Bring up the interface
sudo ip link set eth1 up
sudo ip addr flush dev eth1

# 2. Assign IP Addresses
sudo ip addr add 10.101.1.2/24 dev eth1
sudo ip addr add fc00:0:101:1::2/64 dev eth1

# 3. Add Routes
sudo ip route add 10.0.0.0/24 via 10.101.1.1 dev eth1
sudo ip route add 10.107.1.0/24 via 10.101.1.1 dev eth1
sudo ip route add 10.1.1.0/24 via 10.101.1.1 dev eth1
sudo ip route add 40.0.0.0/24 via 10.101.1.1 dev eth1
sudo ip route add 50.0.0.0/24 via 10.101.1.1 dev eth1

sudo ip -6 route add fc00:0::/32 via fc00:0:101:1::1 dev eth1
sudo ip -6 route add fc00:0:40::1/64 via fc00:0:101:1::1 dev eth1
sudo ip -6 route add fc00:0:50::1/64 via fc00:0:101:1::1 dev eth1