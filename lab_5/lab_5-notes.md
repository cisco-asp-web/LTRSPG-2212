
IP route add
```
ip -6 route add 2001:db8:1002::/64 encap seg6 mode encap.red segs fc00:0:1004:1001:1006:fe06:: dev net1
```

Import image
```
sudo ctr -n k8s.io images import srv6-pytorch.tar
```