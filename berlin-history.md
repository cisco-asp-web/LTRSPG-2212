ip route add fcbb:0:0800:1::/64 encap seg6 mode encap.red segs  fc00:0:1004:1001:1005:fe06:: dev net1


dcloud-rtp-anyconnect.cicsco.com

CLEU topology host history:

 1854  sudo qemu-img resize berlin-vm1.qcow2 40G
 1855  sudo qemu-img resize berlin-vm2.qcow2 40G
 1856  virsh start berlin-vm1 
 1857  virsh start berlin-vm2
 1858  ssh cisco@192.168.122.100
 1859  ssh brmcdoug@192.168.122.100
 1860  ssh cisco@192.168.122.100
 1861  df -h
 1862  docker images
 1863  history | grep du
 1864  sudo du -h --max-depth=2 /var/ 2>/dev/null | sort -hr | head -20
 1865  cd /var/lib/docker
 1866  sudo cd /var/lib/docker
 1867  sudo su
 1868  sudo du -h --max-depth=2 /var/lib/docker 2>/dev/null | sort -hr | head -20
 1869  df -h
 1870  docker container prune -f
 1871  df -h
 1872  docker volume prune -f
 1873  docker images
 1874  docker system df
 1875  docker system df -v
 1876  docker system df
 1877  docker builder prune -a -f
 1878  df -h
 1879  docker images
 1880  docker image rm amsterdam:latest
 1881  docker images
 1882  df -h
 1883  docker image rm rome:latest 
 1884  df -h
 1885  ssh cisco@192.168.122.101
 1886  cd images/
 1887  ls
 1888  sftp cisco@192.168.122.101
 1889  ssh cisco@192.168.122.101
 1890  virsh list --al
 1891  virsh list --all
 1892  virsh shutdown berlin-vm2
 1893  virsh shutdown berlin-vm1
 1894  virsh list --all
 1895  history | grep img
 1896  df -h
 1897  ls -lh
 1898  rm pytorch-srv6-demo.tar 
 1899  df -h
 1900  sudo qemu-img resize berlin-vm1.qcow2 +10G
 1901  sudo qemu-img resize berlin-vm2.qcow2 +10G
 1902  sudo qemu-img info  berlin-vm2.qcow2
 1903  virsh start berlin-vm1 
 1904  virsh start berlin-vm2
 1905  ls
 1906  cd LTRSPG-2212/
 1907  git pull
 1908  cd lab_5/
 1909  ls
 1910  cd pytorch-plugin/
 1911  docker images
 1912  docker build -t pytorch-srv6-demo:latest .
 1913  docker images
 1914  docker tage 6589625e63a8 pytorch-srv6-demo:orig
 1915  docker tag 6589625e63a8 pytorch-srv6-demo:orig
 1916  docker images
 1917  docker run -it pytorch-srv6-demo:latest sh
 1918  docker run -it pytorch-srv6-demo:latest ls -la /app
 1919  docker run -it pytorch-srv6-demo:latest more /app/entrypoint.sh
 1920  cd ~/images/
 1921  ls
 1922  docker save pytorch-srv6-demo:latest > pytorch-srv6-demo.tar


CLEU london-vm-00 history:

  335  sudo hostnamectl hostname london-vm-00
  336  sudo vi /etc/hosts
  337  sudo vi /etc/netplan/10-london-vm-00.yaml
  338  exit
  339  ip route
  340  sudo ip route del default via 198.18.4.3 dev ens4
  341  ip a
  342  sudo rm /etc/netplan/10-berlin.yaml 
  343  sudo netplan apply
  344  ip a
  345  kubectl get nodes -o wide
  346  sudo kubeadm reset
  347  sudo growpart /dev/vda 3
  348  ip a
  349  exit
  350  sudo growpart /dev/vda 3
  351  sudo pvresize /dev/vda3
  352  sudo resize2fs /dev/ubuntu-vg/ubuntu-lv


CRI image import

 243  sudo ctr -n k8s.io images import srv6-pytorch.tar
  244  df -h
  245  rm srv6-pytorch.tar 
  246  df -h
  247  ls
  248  ls images/
  249  exit
  250  sudo ctr -n k8s.io images ls | grep srv6
  251  df -h
  252  sudo ctr -n k8s.io images rm docker.io/library/pytorch-srv6-demo:latest
  253  df -h
  254  sudo ctr -n k8s.io images rm docker.io/library/pytorch-srv6-demo:latest
  255  df -h
  256  sudo ctr -n k8s.io images rm docker.io/library/pytorch-srv6-demo:latest
  257  df -h
  258  sudo du -sh /var/lib/containerd/*
  259  sudo du -sh /var/lib/containerd/
  260  sudo ctr -n k8s.io images ls
  261  sudo ctr namespaces ls
  262  sudo ctr -n default images ls
  263  sudo ctr -n k8s.io images ls -q | xargs -I {} sudo ctr -n k8s.io images rm {}
  264  df -h
  265  sudo crictl images
  266  sudo du -sh /var/lib/containerd/
  267  df -h
  268  exit
  269  cd images/
  270  ls
  271  sudo ctr -n k8s.io images import pytorch-srv6-demo.tar 
  272  sudo ctr -n k8s.io images ls -q | xargs -I {} sudo ctr -n k8s.io images rm {}
  273  df -h
  274  history | grep ctr
  275  sudo ctr -n k8s.io images ls | grep srv6
  276  exit
  277  df -h
  278  ls
  279  cd images/
  280  ls
  281  df -h
  282  ls
  283  rm pytorch-srv6-demo.tar 
  284  df -h
  285  sudo systemctl restart kubelet
  286  kubectl get nodes
  287  ls -la /etc/cni/net.d/
  288  sudo rm /etc/cni/net.d/00-multus.conflist.disabled 
  289  sudo cat /etc/cni/net.d/00-multus.conf
  290  sudo ip -6 addr del fcbb:0:0800:1::/64 dev ens5


