
Host00
```
docker exec -it clab-sonic-host00 ip -6 route add 2001:db8:1002::/64 encap seg6 mode encap.red segs  fc00:0:1200:1001:1202:fe06:: dev eth1
```


```
kubectl exec -it multus-test-01 -- ip -6 route add fcbb:0:800:ffff::103/128 encap seg6 mode encap.red segs  fc00:0:1004:1000:1005:fe06:: dev net1
```