### reference: https://thenewstack.io/how-to-deploy-kubernetes-with-kubeadm-and-containerd/

These instructions have been verified on Ubuntu 20.04 and 22.04

1. turn off swap and set data/time:
```
sudo timedatectl set-timezone America/Los_Angeles
sudo swapoff -a
sudo rm /swap.img
```

2. Edit /etc/fstab, comment out swap
3. apt update/upgrade
```
sudo apt update 
sudo apt upgrade -y
```

4. add curl/https packages, keys, etc.
```
sudo apt install bridge-utils curl apt-transport-https -y
```
```
sudo mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.32/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.32/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo chmod 644 /etc/apt/sources.list.d/kubernetes.list 
sudo apt update
```

5. apt install kubernetes:
``` 
sudo apt -y install kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

6. enable kubelet, modprobes:
```
sudo systemctl enable --now kubelet
sudo modprobe overlay
sudo modprobe br_netfilter
```
7. edit sysctl.conf
```
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding=1
```
```
sudo sysctl -p
```

7. install containerd and runc
```
wget https://github.com/containerd/containerd/releases/download/v1.7.27/containerd-1.7.27-linux-amd64.tar.gz 
wget https://raw.githubusercontent.com/containerd/containerd/main/containerd.service
sudo tar Cxzvf /usr/local containerd-1.7.27-linux-amd64.tar.gz 

sudo cp containerd.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now containerd

sudo systemctl status containerd

wget https://github.com/opencontainers/runc/releases/download/v1.2.6/runc.amd64
sudo  install -m 755 runc.amd64 /usr/local/sbin/runc
```

8. containerd config [from containerd-config.toml](./cilium/containerd-config.toml)
```
sudo mkdir /etc/containerd
sudo cp containerd-config.toml /etc/containerd/config.toml
```

9.  You may now initialize your k8s cluster with kubeadm init 

## Appendix

Kubeadm Join if we want to add a worker node to Berlin cluster:
```
kubeadm join 198.18.4.2:6443 --token cecn5b.n5m612yx1ou17mvz \
	--discovery-token-ca-cert-hash sha256:2c0445b6f4f80069221f666677d43273719533073bf19207395ccd7123531ff8
```

Untaint control plane
```
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```

Annotate
```
kubectl annotate node berlin cilium.io/bgp-virtual-router.65000="router-id=198.18.4.2"
```