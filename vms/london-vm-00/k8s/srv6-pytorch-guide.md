### SRv6 PyTorch Guide

1. Deploy debug pods

```bash
kubectl apply -f srv6-pytorch-debug-pods.yaml
kubectl get pods -o wide
```

2. Check both pods have a Multus-provided net1 interface with IPv6 and route to SRv6 uSID block
```bash
kubectl exec srv6-debug-0 -- ip addr show net1
kubectl exec srv6-debug-1 -- ip addr show net1

kubectl exec srv6-debug-0 -- ip -6 route show fcbb::/32
kubectl exec srv6-debug-1 -- ip -6 route show fcbb::/32
```

3. Test connectivity between pods on backend network
```bash
kubectl exec srv6-debug-0 -- ping6 -c 3 fcbb:0:0800:1::
```

4. Add a static route with SRv6 encap
```bash
kubectl exec srv6-debug-0 -- ip route add fcbb:0:0800:1::/64 encap seg6 mode encap.red segs fcbb:0:1004:1001:1005:fe06:: dev net1

kubectl exec srv6-debug-1 -- ip route add fcbb:0:0800:0::/64 encap seg6 mode encap.red segs fcbb:0:1005:1001:1004:fe06:: dev net1
```

5. Test connectivity with SRv6 encap
```bash
kubectl exec srv6-debug-0 -- ping6 fcbb:0:800:1:: -i .3
```

6. Optional - tcpdump on Containerlab host to see encapsulated packets
```bash
sudo ip netns exec clab-cleu26-spine01 tcpdump -ni eth2
```

### Deploy the SRv6 PyTorch training pods
```bash
kubectl delete -f srv6-pytorch-debug-pods.yaml
kubectl apply -f srv6-pytorch-training-test.yaml
kubectl logs -f srv6-pytorch-0
```

### Deploy training pods

```bash
kubectl delete -f srv6-pytorch-debug-pods.yaml
kubectl apply -f srv6-pytorch-training-test.yaml
```