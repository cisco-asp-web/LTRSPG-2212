# Lab 3: SRv6 for Kubernetes with Cilium [30 Min]

### Description
Now that we've established SRv6 L3VPNs across our network, we're going to transition from **router-based SRv6** to **host-based SRv6**. Our first step will be to enable *SRv6 L3VPN for Kubernetes*. The London VMs have Kubernetes pre-installed and are running the *Cilium CNI* (Container Network Interface). In this lab we'll review some basic Kubernetes commands (kubectl) and then we'll setup Cilium BGP peering with our XRd route reflectors. After that we'll configure Cilium's SRv6 SID manager and Locator pool. Finally we'll add a couple containers to our London K8s cluster and join them to the carrots VRF.

> [!NOTE]
> This portion of the lab makes use of Cilium Enterprise as the SRv6 features not available in the open source version. If you are interested in SRv6 on Cilium or other Enterprise features, please contact the relevant Cisco Isovalent sales team.  

Isovalent has also published a number of labs covering a range of Cilium, Hubble, Tetragon, and Isovalent Load Balancer products and capabilities here:

https://cilium.io/labs/


## Contents
- [Lab 3: SRv6 for Kubernetes with Cilium \[30 Min\]](#lab-3-srv6-for-kubernetes-with-cilium-30-min)
    - [Description](#description)
  - [Contents](#contents)
  - [Lab Objectives](#lab-objectives)
  - [Verify pre-installed Kubernetes and Cilium are running](#verify-pre-installed-kubernetes-and-cilium-are-running)
  - [Kubernetes Custom Resource Definitions (CRDs)](#kubernetes-custom-resource-definitions-crds)
  - [Cilium BGP](#cilium-bgp)
    - [Configure Cilium BGP](#configure-cilium-bgp)
    - [Verify Cilium BGP peering and prefix advertisement](#verify-cilium-bgp-peering-and-prefix-advertisement)
  - [Cilium SRv6](#cilium-srv6)
    - [Cilium SRv6 SID Manager and Locators](#cilium-srv6-sid-manager-and-locators)
  - [Cilium VRF](#cilium-vrf)
    - [Create the carrots BGP VRF](#create-the-carrots-bgp-vrf)
  - [Verify Cilium VRFs and Create Pods](#verify-cilium-vrfs-and-create-pods)
  - [Verify Cilium advertised L3VPN prefixes in the lab](#verify-cilium-advertised-l3vpn-prefixes-in-the-lab)
    - [Run a ping test!](#run-a-ping-test)
    - [Optional - Traffic capture using Edgeshark](#optional---traffic-capture-using-edgeshark)
  - [Lab 3 Appendix](#lab-3-appendix)
  - [End of lab 3](#end-of-lab-3)

## Lab Objectives
We will have achieved the following objectives upon completion of Lab 3:

* Understanding of Cilium networking for Kubernetes
* Understanding on how to configure Cilium BGP, VRFs, and SRv6

  
## Verify pre-installed Kubernetes and Cilium are running

The **london-vm-00** is our Kubernetes control plane node.  All of the following steps are to be performed on **london-vm-00**   unless otherwise specified.

1. Open a terminal session on the **topology-host** and SSH to **london-vm-00**
   ```
   ssh cisco@london-vm-00
   ```

2. Run a couple commands to verify the K8s cluster and the Cilium Installation

   Display k8s nodes:
   ```
   kubectl get nodes -o wide
   ```
   
   The ouput should look something like:
   ```yaml
   $ kubectl get nodes -o wide
   NAME           STATUS   ROLES           AGE     VERSION   INTERNAL-IP   EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION       CONTAINER-RUNTIME
   london-vm-00   Ready    control-plane   6d      v1.35.0   10.8.0.2      <none>        Ubuntu 22.04.5 LTS   5.15.0-164-generic   containerd://1.7.27
   london-vm-01   Ready    <none>          2d23h   v1.31.8   10.8.1.2      <none>        Ubuntu 22.04.5 LTS   5.15.0-164-generic   containerd://1.7.27
   london-vm-02   Ready    <none>          2d23h   v1.31.8   10.8.2.2      <none>        Ubuntu 22.04.5 LTS   5.15.0-164-generic   containerd://1.7.27
   ```

   Display Cilium pods:
   ```
   kubectl get pods -n kube-system | grep cilium
   ```
   The output should look something like this:
   ```yaml
   $ kubectl get pods -n kube-system | grep cilium
   cilium-envoy-4nmml                     1/1     Running   3 (4h36m ago)   5d23h
   cilium-envoy-5k2k7                     1/1     Running   2 (4h59m ago)   2d23h
   cilium-envoy-6n7tg                     1/1     Running   2 (4h59m ago)   2d23h
   cilium-h6f79                           1/1     Running   1 (4h59m ago)   2d10h
   cilium-node-init-7fkxn                 1/1     Running   2 (4h59m ago)   2d23h
   cilium-node-init-vqp5s                 1/1     Running   3 (4h36m ago)   5d23h
   cilium-node-init-zcsh6                 1/1     Running   2 (4h59m ago)   2d23h
   cilium-operator-74c5c6c5f6-cwjd7       1/1     Running   7 (4h9m ago)    5d23h
   cilium-operator-74c5c6c5f6-hhd4n       1/1     Running   3 (4h36m ago)   5d23h
   cilium-rc6cd                           1/1     Running   1 (4h59m ago)   2d10h
   cilium-vslzk                           1/1     Running   2 (4h36m ago)   2d10h
   ```

  Notes on the pods:
  * `Cilium-envoy`: used as a host proxy for enforcing HTTP and other L7 policies for the cluster. Reference: https://docs.cilium.io/en/latest/security/network/proxy/envoy/
  * `Cilium-node-init`: used to initialize the K8s node and install the Cilium agent.
  * `Cilium-operator`: used to manage the Cilium agent on the node.
  * `Cilium-nnnnn`: the Cilium agent on the node and the element that will perform BGP peering and programming of eBPF SRv6 forwarding policies.


   Display Cilium DaemonSet status:
   ```
   kubectl get ds -n kube-system cilium
   ```
   The output should show three Cilium DaemonSets (ds) available, example:
   ```yaml
   $ kubectl get ds -n kube-system cilium
   NAME     DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR            AGE
   cilium   3         3         3       3            3           kubernetes.io/os=linux   94m
   ```
> [!NOTE]
> A Kubernetes DaemonSet is a feature that ensures a pod runs on all or some nodes in a Kubernetes cluster. DaemonSets are used to deploy background services, such as monitoring agents, network agents (*such as Cilium/eBPF*), log collectors, and storage volumes.

Now we're ready!

##  Kubernetes Custom Resource Definitions (CRDs)

Per: https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/

*A custom resource is an extension of the Kubernetes API that is not necessarily available in a default Kubernetes installation. Many core Kubernetes functions are now built using custom resources, making Kubernetes more modular.*

Said another way, CRDs enable us to add, update, or delete Kubernetes cluster elements and their configurations. The add/update/delete action might apply to the cluster as a whole, a node in the cluster, an aspect of cluster networking or other elements within the cluster like pods, services, daemonsets, etc.

A CRD applied to a single element in the K8s cluster would be analogous to configuring BGP on a router. A CRD applied to multiple elements or cluster-wide would be analogous to adding BGP route-reflection to a network. 

CRDs come in YAML file format and in the next several sections of this lab we'll apply CRDs to the K8s cluster to setup Cilium BGP peering, establish Cilium SRv6 locator ranges, create VRFs, etc.

One of the great things about CRDs is you can combine all the configuration elements into a single file, or you can break it up into multiple files by configuration element. We've grouped roughly 10 CRDs into three yaml files:

   * [01-cilium-bgp.yaml](cilium/01-cilium-bgp.yaml) - Full Cilium BGP config including ASN, peers, address-families, node-override/update-source, and prefix advertisement
   * [02-cilium-srv6.yaml](cilium/02-cilium-srv6.yaml) - Cilium SRv6 SID manager and Locator pool configuration
   * [03-carrots-vrf.yaml](cilium/07-vrf-carrots.yaml) - Cilium BGP and K8s VRF 'carrots' configuration and deployment of test pod

On **london-vm-00** change to the lab_3/cilium directory and check out the contents
   ```
   cd ~/LTRSPG-2212/lab_3/cilium/
   ll
   ```

The directory also contains [99-cilium-all.yaml](./cilium/99-cilium-all.yaml) which has all CRDs used in this lab. This file can be used to deploy all elements in a single shot, or to clean out all Cilium BGP/SRv6/VRF config.
  

## Cilium BGP

For the sake of simplicity we'll use iBGP peering between our London K8s nodes and our route reflectors **paris xrd05** and **barcelona xrd06**. 

![Cilium SRv6 L3VPN](/topo_drawings/lab3-cilium-l3vpn-topology.png)

Our Cilium BGP configuration is broken into four CRDs:

1. The *BGP Cluster Config CRD* where we define BGP global values like ASN, etc.
   
   Here is a portion of the BGP Cluster Config CRD with notes:
   ```yaml
   apiVersion: isovalent.com/v1alpha1
   kind: IsovalentBGPClusterConfig  # the BGP cluster configuration CRD  
   metadata:
     name: cilium-bgp 
   spec:
     nodeSelector:
       matchExpressions:
       - key: kubernetes.io/hostname
         operator: In                      # apply config to all nodes in the values list
         values:
         - london-vm-00
         - london-vm-01
         - london-vm-02   
     bgpInstances:                         # the k8s cluster could have multiple BGP instances
     - name: "asn65000"                    # for simplicity we're using the same ASN as our XRd network
       localASN: 65000
       peers:
       - name: "paris-rr"                  # base peering config
         peerASN: 65000                   
         peerAddress: fc00:0:5555::1       
         peerConfigRef:
           name: "cilium-peer"             # reference to additional peer config in another CRD
       - name: "barcelona-rr"
         peerASN: 65000
         peerAddress: fc00:0:6666::1
         peerConfigRef:
           name: "cilium-peer"
   ```

2. The *BGP Peer Config CRD* is where we control address families and other BGP peering or route policies on a per peer or peer-group basis.

   Here is a portion of the BGP Peer Config CRD with notes:
   ```yaml
   metadata:
     name: cilium-peer    # name of the peer-group
   spec:
     families:            # afi/safi address family combinations
       - afi: ipv6
         safi: unicast
         advertisements:
           matchLabels:
             advertise: "bgpv6unicast"   # advertise ipv6 prefixes found in the bgpv6unicast advertisement CRD
       - afi: ipv4
         safi: mpls_vpn  # a bit of a misnomer, we're advertising SRv6 L3VPN, or the equivalent of vpnv4 unicast in XR
   ```

3. The *BGP Node Config Override CRD* which includes the *`localAddress`* parameter. This parameter tells Cilium which source address to use for its BGP peering sessions, similar to `update-source` in IOS-XR.

   Here is a portion of the node override CRD with notes:
   ```yaml
    metadata:
      name: london-vm-00     # this CRD will apply to the london-vm-00 node
    spec:
      bgpInstances:
        - name: "asn65000"        
          srv6Responder: true   # instructs BGP to advertise the node's SRv6 Locator (we'll create the locator a few steps after this)
          peers:
            - name: "paris-rr"              # must match the name of the peer in the cluster config
              localAddress: fc00:0:800::2   # the source address to use for the peering session
   ```

4. The *BGP Prefix Config CRD* which defines prefix advertisements and policies
  
   Here is a portion of the prefix advertisement CRD with notes:
   ```yaml
    metadata:
      name: bgp-ipv6-unicast
      labels:
        advertise: bgpv6unicast     # this label will be used by the peer config CRD for prefixes to advertise
    spec:
      advertisements:                           
        - advertisementType: "SRv6LocatorPool" # advertise the SRv6 locator pool (to be created a few steps after this)
          selector:
            matchLabels:
              export: "pool0"
        - advertisementType: "PodCIDR"          # advertise the pod CIDR prefix for pods in the default VRF
   ```

### Configure Cilium BGP
1. On **london-vm-00** apply the *Cilium BGP Config CRD*. This config establishes BGP peering on all three **london-vms** with the route reflectors **paris-xrd05** and **barcelona-xrd06**.
   ```
   kubectl apply -f 01-cilium-bgp.yaml
   ```

   Expected output:
   ```
    isovalentbgppeerconfig.isovalent.com/cilium-peer created
    isovalentbgpnodeconfigoverride.isovalent.com/london-vm-00 created
    isovalentbgpnodeconfigoverride.isovalent.com/london-vm-01 created
    isovalentbgpnodeconfigoverride.isovalent.com/london-vm-02 created
    isovalentbgpadvertisement.isovalent.com/bgp-ipv6-unicast created
   ```
   

### Verify Cilium BGP peering and prefix advertisement

> [!NOTE]
> the **paris** and **barcelona**' route-reflectors were preconfigured to peer with the Cilium nodes and inherited the vpnv4 address family configuration during Lab 2, so we don't need to update their configs. 


1. Use the *`cilium bgp peers`* command to verify established peering sessions with **paris xrd05** and **barcelona xrd06**. Note, it may take a few seconds to a minute for the peering sessions and bgp table sync.
   
   ```
   cilium bgp peers
   ```

   We expect each london VM to have two IPv6 BGP peering sessions established and receiving BGP NLRIs for IPv6 and IPv4/mpls_vpn (aka, SRv6 L3VPN). We also expect to be advertising an IPv6 unicast prefix, but not advertise VPN prefixes yet.

   Partial output:
   ```yaml
   $ cilium bgp peers
   Node          Local AS  Peer AS  Peer Address     Session State  Uptime  Family          Received  Advertised
   london-vm-00  65000     65000    fc00:0:5555::1   established    25s     ipv6/unicast    6         1    
                                                                            ipv4/mpls_vpn   4         0    
                 65000     65000    fc00:0:6666::1   established    30s     ipv6/unicast    6         1    
                                                                            ipv4/mpls_vpn   4         0
   <snip>  
   ```                                                                        

2. Let's get a little more detail on advertised prefixes with the `cilium bgp routes` command. Let's first add a -h flag to see our options

   ```
   cilium bgp routes -h
   ```

   Example output:
   ```
   $ cilium bgp routes -h
   Lists BGP routes from all nodes in the cluster

   Usage:
     cilium bgp routes <available | advertised> <afi> <safi> [vrouter <asn>] [peer|neighbor <address>] [flags]
   ```

3. Let's get the advertised IPv6 prefixes:
   ```
   cilium bgp routes advertised ipv6 unicast
   ```

   Example partial output showing **london-vm-00's** network-facing interface as the BGP NextHop
   ```yaml
   Node         VRouter  Peer            Prefix            NextHop        Age       Attrs
   london-vm-00  65000    fc00:0:5555::1  2001:db8:42::/64  fc00:0:800::2  3h22m34s  [{Origin: i} {AsPath: } {LocalPref: 100} {MpReach(ipv6-unicast): {Nexthop: fc00:0:800::2, NLRIs: [2001:db8:42::/64]}}]       
                 65000    fc00:0:6666::1  2001:db8:42::/64  fc00:0:800::2  3h22m34s  [{Origin: i} {AsPath: } {LocalPref: 100} {MpReach(ipv6-unicast): {Nexthop: fc00:0:800::2, NLRIs: [2001:db8:42::/64]}}]
   ```
## Cilium SRv6

### Cilium SRv6 SID Manager and Locators
Per Cilium Enterprise documentation:
*The SID Manager manages a cluster-wide pool of SRv6 locator prefixes. You can define a prefix pool using the IsovalentSRv6LocatorPool CRD and the Cilium Operator will assign a locator for each node from this prefix.*

In the next step we will configure a /40 range from which Cilium will allocate a /48 bit SRv6 locator to each node in the London K8s cluster.

Cilium also supports /64 locators, but for simplicity and consistency with our *xrd* nodes we're going to use the very commonly deployed /48 bit locators. Here is the yaml file CRD with notes:

   ```yaml
   apiVersion: isovalent.com/v1alpha1
   kind: IsovalentSRv6LocatorPool
   metadata:
     name: pool0
     labels:
       export: "pool0"         # label for our BGP prefix advertisement CRD to match on
   behaviorType: uSID          # options are uSID or SRH
   prefix: fc00:0:8800::/40    # the larger /40 block from which a /48 would be allocated to each node in the cluster
   structure:
     locatorBlockLenBits: 32   # the uSID block length
     locatorNodeLenBits: 16    # the uSID node length - here 32 + 16 results in our /48 bit Locator
     functionLenBits: 16
     argumentLenBits: 0
   ```

1. Create the Cilium SRv6 locator pool. The full CRD may be reviewed here: [02-cilium-srv6.yaml](cilium/02-cilium-srv6.yaml)
  
   ```
   kubectl apply -f 02-cilium-srv6.yaml
   ```

   Recall the *`BGP prefix advertisement CRD`* included a spec for advertising the SRv6 locator pool as well:
   ```diff
     advertisements:
       - advertisementType: "SRv6LocatorPool"  
         selector:
           matchLabels:
   +          export: "pool0"
   ```

2. Now that we have an SRv6 locator pool defined, let's check our BGP advertised prefixes again:
   ```
   cilium bgp routes advertised ipv6 unicast
   ```

   Example partial output, Cilium is now advertising the node's Locators as highlighted below. Also, due to the dynamic nature of the allocation your /48 values will differ from the example output:
   ```diff
   Node           VRouter   Peer             Prefix               NextHop           Age     Attrs
   london-vm-00   65000     fc00:0:5555::1   2001:db8:42::/64     fc00:0:800::2           
                  65000     fc00:0:6666::1   2001:db8:42::/64     fc00:0:800::2            
   +              65000     fc00:0:5555::1   fc00:0:88f7::/48     fc00:0:800::2           
   +              65000     fc00:0:6666::1   fc00:0:88f7::/48     fc00:0:800::2    
   ```

3. Validate the locator pool:
   ```
   kubectl get sidmanager -o yaml
   ```
   
   Or for a more concise output:
   ```
   kubectl get sidmanager -o custom-columns="NAME:.metadata.name,ALLOCATIONS:.spec.locatorAllocations"
   ```

   The truncated output below shows the Cilium uSID locator allocation for each node. Notice that we have the
   same prefix as the previous command *fc00:0:88f7::/48* listed for **london-vm-00**.

   Example output:

   ```diff
   NAME           ALLOCATIONS
   + london-vm-00   [map[locators:[map[behaviorType:uSID prefix:fc00:0:88f7::/48
     london-vm-01   [map[locators:[map[behaviorType:uSID prefix:fc00:0:88f6::/48 
     london-vm-02   [map[locators:[map[behaviorType:uSID prefix:fc00:0:8804::/48
   ```

## Cilium VRF

### Create the carrots BGP VRF
You will be applying the full Cilium VRF configuration [03-carrots-vrf.yaml](cilium/03-carrots-vrf.yaml) shortly.

First though lets look at the BGP VRF configuration section contained in *03-carrots-vrf.yaml* 

  ```yaml
  ---
  apiVersion: isovalent.com/v1
  kind: IsovalentBGPVRFConfig      # the BGP VRF configuration CRD
  metadata:
    name: carrots-config   # a meta data label / name of the vrf config
  spec:
    families:
      - afi: ipv4        
        safi: mpls_vpn   
        advertisements:
          matchLabels:
            advertise: "bgp-carrots"  # a meta data label / name for the route advertisement - this is analogous to a outbound route policy

  ---
  apiVersion: isovalent.com/v1
  kind: IsovalentBGPAdvertisement      # BGP route advertisement CRD
  metadata:
    name: carrots-adverts     # a meta data label / name for the VRF route advertisement
    labels:
      advertise: bgp-carrots  # matches the VRF config label
  spec:
    advertisements:
      - advertisementType: "PodCIDR"   # we're going to advertise the k8s pod CIDR or subnet
  ```

Now lets dive deeper into the  *carrots* VRF and the Alpine linux container in the VRF. The goal is to create a forwarding policy so that packets from the container get placed into the *carrots* vrf and then encapsulated in an SRv6 L3VPN header as detailed in the below diagram.

![Cilium SRv6 L3VPN](/topo_drawings/cilium-packet-forwarding.png)

A brief explanation of the VRF and pods CRD configuration section containted in *03-carrots-vrf.yaml*

```yaml
---
apiVersion: v1
kind: Namespace   # we're creating a new k8s namespace
metadata:
  name: veggies   # called veggies
  labels:
    name: veggies

---
apiVersion: isovalent.com/v1alpha
kind: IsovalentVRF         
metadata:
  name: carrots
spec:
  vrfID: 99                  # the VRF ID - analogous to the Route Distinguisher on a router
  locatorPoolRef: pool0       # use our previously created SRv6 locator pool
  rules:
  - selectors:
    - endpointSelector:
        matchLabels:
          vrf: carrots    # analogous to the RT import/export policy on a router
    destinationCIDRs:
    - 0.0.0.0/0

---
apiVersion: v1
kind: Pod   # we're creating a new k8s pod
metadata:
  namespace: veggies   # the pod is in the veggies namespace
  labels:
    app: alpine-ping
    vrf: carrots   # the pod is in the carrots VRF
  name: carrots0   # the pod's name
spec:
  nodeName: london-vm-02  # explicitly assign this pod to london-vm-02 (for later steps in the lab)
  containers:
  - image: alpine:latest   # deploy the pod using a super lightweight container image
    imagePullPolicy: IfNotPresent
    name: carrots0
    command:
      - /bin/sh
      - "-c"
      - "sleep 60m"
```

1. Apply the carrots Cilium VRF configuration:
   ```
   kubectl apply -f 03-carrots-vrf.yaml
   ```

## Verify Cilium VRFs and Create Pods

You'll note that the pod is in the *carrots VRF* and the K8s namespace *veggies*. We didn't do this to be overly complex, but rather to illustrate the fact that the namespace and VRF are independent of each other. We could have pods from multiple namespaces in the same VRF and vice versa.

1. Verify the VRF carrots pods are running:
   ```
   kubectl get pods -n veggies
   ```

   Expected output:
   ```
   NAME      READY   STATUS    RESTARTS   AGE
   carrots0   1/1     Running   0          10s
   ``` 

2. Let's get the pods' IP addresses as we'll need them in a few more steps:
   ```
   kubectl get pod -n veggies carrots0 -o jsonpath="Node: {.spec.nodeName} | IPs: {.status.podIPs[*].ip}" && echo
   ```

   Expected output should look something like the below with the pod being deployed to **london-vm-02** with dynamically assigned IP addresses:
   ```
   Node: london-vm-02 | IPs: 10.200.2.46 2001:db8:42:4::af86
   ```

3. Next we'll verify Cilium has allocated the carrots VRF a SRv6 L3VPN uDT4 SID on **london-vm-02**:
   ```
   kubectl get sidmanager london-vm-02 -o yaml
   ```

   Or a much longer command can give us clean abbreviated output:
   ```
   echo && kubectl get sidmanager london-vm-02 -o jsonpath="Host: {.metadata.name} | VRF: {.status.sidAllocations[*].sids[*].metadata} | SID: {.status.sidAllocations[*].sids[*].sid.addr} | Behavior: {.status.sidAllocations[*].sids[*].behavior}" && echo
   ```

   Example output:
   ```
   Host: london-vm-02 | VRF: carrots | SID: fc00:0:88d2:1530:: | Behavior: uDT4
   ```

## Verify Cilium advertised L3VPN prefixes in the lab

1. Using the containerlab extension, ssh to **rome xrd07** and run some BGP verification commands.

   ```
   show bgp vpnv4 unicast | include 10.200.
   ```
   ```
   show bgp vpnv4 unicast rd 9:9 10.200.2.0/24
   ```

   In the output of the first command we expect to find the Cilium advertised L3VPN prefixes, example:
   ```
   *>i10.200.2.0/24      fc00:0:800:2::2                100      0 ?
   ```

   In the output of the second command we expect to see detailed information for the prefix. Below is truncated output. Note, due to Cilium's dynamic allocation, your *Received Label* and *Sid* values will most likely differ from this example:
   ```diff
    fc00:0:800:2::2 (metric 4) from fc00:0:6666::1 (10.8.2.2)
   +   Received Label 0x15300
      Origin incomplete, localpref 100, valid, internal, not-in-vrf
      Received Path ID 0, Local Path ID 0, version 0
      Extended community: RT:9:9 
      Originator: 10.8.2.2, Cluster list: 10.0.0.6
      PSID-Type:L3, SubTLV Count:1
       SubTLV:
   +     T:1(Sid information), Sid:fc00:0:88d2::(Transposed), Behavior:63, SS-TLV Count:1
         SubSubTLV:
          T:1(Sid structure):
   ```

2. Back on **london-vm-00**, verify SRv6 Egress Policies. This command will give you a rough equivalent to the SRv6 L3VPN FIB table
   ```
   kubectl get IsovalentSRv6EgressPolicy -o yaml
   ```

   Or for abbreviated output:
   ```
   kubectl get IsovalentSRv6EgressPolicy -o jsonpath="{.items[*].spec}" | jq
   ```

   Example of partial output:
   ```
   {
      "destinationCIDRs": [
        "10.101.1.0/24"
      ],
      "destinationSID": "fc00:0:1111:e009::",
      "vrfID": 99
   }
   {
      "destinationCIDRs": [
        "10.107.2.0/24"
      ],
      "destinationSID": "fc00:0:7777:e006::",
      "vrfID": 99
   }
   ```

### Run a ping test!

1. From **london-vm-00** exec into the *`carrots`* pod and ping Rome's interface in the carrots VRF:
    ```
    kubectl exec -it -n veggies carrots0 -- sh
    ```
    ```
    ping 10.107.1.2 -i .5
    ```
    
    or
    ```
    kubectl exec -it -n veggies carrots0 -- ping 10.107.1.2 -i .5
    ```

### Optional - Traffic capture using Edgeshark

The London VMs are connected to the Containerlab topology via Linux bridge instances. You can inspect traffic either at the source (on the bridge) or at the destination (Rome container’s eth2).

To capture traffic near the source:
   - Open Firefox
   - Go to EdgeShark (http://198.18.133.100:5001/w)
   - Click Refresh
   - Select the desired interface to start the capture.

![Edgeshark on the linux bridge](../topo_drawings/lab33edgeshark-linux-bridge.png)

or use the containerlab extension to capture the traffic on Rome's eth2 interface as we previously executed in lab 1 and 2 



> [!NOTE]
> In a future version of this lab we hope to add support for Cilium SRv6-TE. 

## Lab 3 Appendix
We have provided some additional cilium and kubernetes commands in an appendix: [Lab 3 Appendix](https://github.com/cisco-asp-web/LTRSPG-2212/blob/main/lab_3/lab_3-appendix.md)

## End of lab 3
Please proceed to [Lab 4](https://github.com/cisco-asp-web/LTRSPG-2212/blob/main/lab_4/lab_4-guide.md)

