#!/bin/bash

sudo ip netns exec clab-cleu26-xrd-london tc qdisc add dev Gi0-0-0-1 root netem delay 10000
sudo ip netns exec clab-cleu26-xrd-london tc qdisc add dev Gi0-0-0-2 root netem delay 5000

sudo ip netns exec clab-cleu26-xrd-amsterdam tc qdisc add dev Gi0-0-0-1 root netem delay 30000
sudo ip netns exec clab-cleu26-xrd-amsterdam tc qdisc add dev Gi0-0-0-2 root netem delay 20000

sudo ip netns exec clab-cleu26-xrd-berlin tc qdisc add dev Gi0-0-0-1 root netem delay 40000

sudo ip netns exec clab-cleu26-xrd-zurich tc qdisc add dev Gi0-0-0-1 root netem delay 30000
sudo ip netns exec clab-cleu26-xrd-zurich tc qdisc add dev Gi0-0-0-2 root netem delay 30000

sudo ip netns exec clab-cleu26-xrd-paris tc qdisc add dev Gi0-0-0-2 root netem delay 5000

sudo ip netns exec clab-cleu26-xrd-barcelona tc qdisc add dev Gi0-0-0-0 root netem delay 30000

echo "Latencies added. The following output applies in both directions, Ex: xrd-london -> xrd-amsterdam and xrd-amsterdam -> xrd-london"

echo "xrd-london link latency: "
sudo ip netns exec clab-cleu26-xrd-london tc qdisc list | grep delay
echo "xrd-amsterdam link latency: "
sudo ip netns exec clab-cleu26-xrd-amsterdam tc qdisc list | grep delay
echo "xrd-berlin link latency: "
sudo ip netns exec clab-cleu26-xrd-berlin tc qdisc list | grep delay
echo "xrd-zurich link latency: "
sudo ip netns exec clab-cleu26-xrd-zurich tc qdisc list | grep delay
echo "xrd-paris link latency: "
sudo ip netns exec clab-cleu26-xrd-paris tc qdisc list | grep delay
echo "xrd-barcelona link latency: "
sudo ip netns exec clab-cleu26-xrd-barcelona tc qdisc list | grep delay


