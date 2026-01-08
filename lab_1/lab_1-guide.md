# Lab 1 Guide: Deploy XRd Topology and apply SRv6 configurations [20 Min]

We use of containerlab to orchestrate the XRd and SONiC virtual network topologies in this lab. If you wish to explore XRd and its uses beyond the scope of this lab the xrdocs team has posted a number of tutorials here: 

https://xrdocs.io/virtual-routing/tutorials

For more information on containerlab see:

https://containerlab.dev/


## Contents
- [Lab 1 Guide: Deploy XRd Topology and apply SRv6 configurations \[20 Min\]](#lab-1-guide-deploy-xrd-topology-and-apply-srv6-configurations-20-min)
  - [Contents](#contents)
  - [Lab Objectives](#lab-objectives)
  - [Topology](#topology)
  - [Accessing the routers](#accessing-the-routers)
  - [Launch and Validate XRD Topology](#launch-and-validate-xrd-topology)
    - [Connect to the Topology Host and SSH to Containers.](#connect-to-the-topology-host-and-ssh-to-containers)
    - [Accessing the London K8s Control Plane VM](#accessing-the-london-k8s-control-plane-vm)
  - [Validate ISIS Topology](#validate-isis-topology)
    - [Add Synthetic Latency to the Links](#add-synthetic-latency-to-the-links)
  - [Validate BGP Peering](#validate-bgp-peering)
  - [Configure and Validate SRv6](#configure-and-validate-srv6)
    - [Configure SRv6 on xrd01](#configure-srv6-on-xrd01)
    - [Configure SRv6 on xrd07](#configure-srv6-on-xrd07)
    - [Validate SRv6 configuration and reachability](#validate-srv6-configuration-and-reachability)
  - [End-to-End Connectivity - Edgeshark](#end-to-end-connectivity---edgeshark)
  - [End of Lab 1](#end-of-lab-1)
  
## Lab Objectives
We will have achieved the following objectives upon completion of Lab 1:

* Access all devices in the lab
* Deployed the full network topology (XRd frontend, SONiC backend)
* Basic familiarity with containerlab
* Confirm IPv4 and IPv6 connectivity
* Familiarity with base SRv6 configuration 


## Topology 

For Labs 1 - 3 we will use the topology shown below. In this network we have 7 XRd routers providing SRv6 transport services to a pair of Ubuntu containers (London and Rome) and a Kubernetes cluster running on Ubuntu VMs (London).
![Lab Topology](../topo_drawings/overview-topology-large.png)

Although the topology includes several SONiC routers and virtual machines, this lab focuses exclusively on the WAN network, which is built using IOS-XRd routers.

## Accessing the routers 

⚠️⚠️⚠️  Note: This section is provided for reference only. We will walk through router access during the live demo. ⚠️⚠️⚠️ 

Lab attendees can interact with the routers in multiple ways. They may choose to ssh to the **topology host** VM and use it as a jumpbox to:

- Launch topologies  
- SSH into routers  
- Perform additional configuration tasks

However, it is **recommended** to use **Visual Studio Code** on the provided **Windows virtual machine** for a more streamlined experience.

This environment comes pre-configured with useful extensions such as:

- **Remote-SSH**
- **Containerlab**

These tools allow attendees to:

- Start and manage topologies  
- SSH into routers  
- Access containers  
- Capture traffic easily using **Edgeshark**

This setup simplifies lab operations and significantly enhances usability.

RDP to the Windows Virtual machine from the lab attendee laptop:

The lab can be accessed using a Remote Desktop connection to the windows management hosts at 198.18.128.102 **(admin / cisco123)**

![windows-rdp](.././topo_drawings/windows-rdp.png)


Launch Visual Code:

![launch visual code](../topo_drawings/lab1-visual-code-launch.png)

Visual code will connect to the topology host and lab attendees should enter the "cisco123" password 

![connect using visual code](../topo_drawings/lab1-visual-code-connect.png)

You are now connected to the topology host and can start topologies and inspect traffic. At the moment, no topology is started. Make sure you click on the containerlab extension before you can start a topology.

![connected visual code](../topo_drawings/lab1-visual-code-connected.png)


**User Credentials**
All VMs, routers, etc. use the same user credentials:
```
User: cisco, Password: cisco123
```



## Launch and Validate XRD Topology

The containerlab visual code extension will be used to launch lab 1:

![connected visual code](../topo_drawings/lab1-launch-topology.png)

The icons should turn green to visually indicate that the topology has been successfully deployed in Containerlab.

![connected visual code](../topo_drawings/lab1-topology-launched.png)

We can also verify the containerlab logs in the visual code output window. Truncated example:

```
[DEBUG] Containerlab extension activated.
 00:13:37 INFO Created link: sonic-leaf-02:eth3 ▪┄┄▪ sonic-spine-02:eth3
 00:13:37 INFO Created link: sonic-leaf-02:eth5 ▪┄┄▪ london-vm-02-be:sonic-leaf02-eth5
 00:13:37 INFO Adding host entries path=/etc/hosts
 00:13:37 INFO Adding SSH config for nodes path=/etc/ssh/ssh_config.d/clab-cleu26.conf
 ╭──────────────────────────────────┬─────────────────────────────────────┬────────────────────┬────────────────╮
 │               Name               │              Kind/Image             │        State       │ IPv4/6 Address │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-app-container-london │ linux                               │ running            │ 172.20.6.108   │
 │                                  │ cl-london-container:latest          │                    │ N/A            │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-app-container-rome   │ linux                               │ running            │ 172.20.6.109   │
 │                                  │ cl-rome-container:latest            │                    │ N/A            │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-sonic-leaf-00        │ linux                               │ running            │ 172.20.6.128   │
 │                                  │ vrnetlab/sonic_sonic-vs:vpp20250422 │ (health: starting) │ N/A            │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-sonic-leaf-01        │ linux                               │ running            │ 172.20.6.129   │
 │                                  │ vrnetlab/sonic_sonic-vs:vpp20250422 │ (health: starting) │ N/A            │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-sonic-leaf-02        │ linux                               │ running            │ 172.20.6.130   │
 │                                  │ vrnetlab/sonic_sonic-vs:vpp20250422 │ (health: starting) │ N/A            │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-sonic-spine-00       │ linux                               │ running            │ 172.20.6.192   │
 │                                  │ vrnetlab/sonic_sonic-vs:vpp20250422 │ (health: starting) │ N/A            │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-sonic-spine-01       │ linux                               │ running            │ 172.20.6.193   │
 │                                  │ vrnetlab/sonic_sonic-vs:vpp20250422 │ (health: starting) │ N/A            │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-sonic-spine-02       │ linux                               │ running            │ 172.20.6.194   │
 │                                  │ vrnetlab/sonic_sonic-vs:vpp20250422 │ (health: starting) │ N/A            │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-xrd-amsterdam        │ cisco_xrd                           │ running            │ 172.20.6.102   │
 │                                  │ cisco-xrd-control-plane:24.4.1      │                    │ N/A            │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-xrd-barcelona        │ cisco_xrd                           │ running            │ 172.20.6.106   │
 │                                  │ cisco-xrd-control-plane:24.4.1      │                    │ N/A            │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-xrd-berlin           │ cisco_xrd                           │ running            │ 172.20.6.103   │
 │                                  │ cisco-xrd-control-plane:24.4.1      │                    │ N/A            │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-xrd-london           │ cisco_xrd                           │ running            │ 172.20.6.101   │
 │                                  │ cisco-xrd-control-plane:24.4.1      │                    │ N/A            │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-xrd-paris            │ cisco_xrd                           │ running            │ 172.20.6.105   │
 │                                  │ cisco-xrd-control-plane:24.4.1      │                    │ N/A            │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-xrd-rome             │ cisco_xrd                           │ running            │ 172.20.6.107   │
 │                                  │ cisco-xrd-control-plane:24.4.1      │                    │ N/A            │
 ├──────────────────────────────────┼─────────────────────────────────────┼────────────────────┼────────────────┤
 │ clab-cleu26-xrd-zurich           │ cisco_xrd                           │ running            │ 172.20.6.104   │
 │                                  │ cisco-xrd-control-plane:24.4.1      │                    │ N/A            │
 ╰──────────────────────────────────┴─────────────────────────────────────┴────────────────────┴────────────────╯

```

> [!NOTE]
> All *containerlab* commands can be abbreviated to *clab*. Example: *sudo clab deploy -t lab_1-topology.clab.yaml*

If the terminal is not visible in VScode, please launch a new terminal using the terminal / New terminal tabs. that way, you will be directly connected to the topology host using SSH.


### Connect to the Topology Host and SSH to Containers.

The entire lab is doable from visual code, you should launch a terminal and it will automatically ssh into the topology host.

![terminal visual code](../topo_drawings/lab1-visual-code-terminal.png)

Run a couple commands to verify the docker/router containers are up
```
docker ps -a
sudo containerlab inspect --all
```

![ssh verification](../topo_drawings/lab1-visual-code-ssh-verification.png)



> [!IMPORTANT]
> The XRd router instances should be available for SSH access about 1 - 2 minutes after spin up.


To establish an SSH session to an IOS-XRd router, use the Containerlab Visual Studio Code extension. Right-click on the router and select SSH from the context menu.

![ssh into xrd01](../topo_drawings/lab1-ssh-xrd01.png)


The London and Rome sites host Linux-based containers that will be used to generate traffic and run validation tests throughout the lab. To access these containers, use the same method as for an IOS-XRd router: right-click on the container in the Containerlab VS Code extension, select SSH, and repeat the same procedure.
The same credentials used for the IOS-XRd routers apply.

![Attach terminal](../topo_drawings/lab1-attach-terminal.png)


### Accessing the London K8s Control Plane VM

In our lab the **London VMs** are three Ubuntu Kubernetes nodes running the **Cilium** Container Network Interface (CNI) and connected to the **London** router.


1. From the topology host terminal in visual code, SSH to *London-vm-00* 
    ```
    ssh cisco@london-vm-00
    ```
   
2. Check IPv6 connectivity from **london-vm-00** to **london xrd01**

    ![London xrd01](../topo_drawings/lab1-london-xrd01.png)

    ```
    ping fc00:0:800::1 -c 2
    ```
    ```
    cisco@london-vm-00:~$ ping fc00:0:800::1 -c 2
    PING fc00:0:800::1(fc00:0:800::1) 56 data bytes
    64 bytes from fc00:0:800::1: icmp_seq=1 ttl=64 time=1.61 ms
    64 bytes from fc00:0:800::1: icmp_seq=2 ttl=64 time=1.81 ms

    --- fc00:0:800::1 ping statistics ---
    2 packets transmitted, 2 received, 0% packet loss, time 1001ms
    rtt min/avg/max/mdev = 1.611/1.709/1.808/0.098 ms
    ```

    Visual representation:

    ![berlin connectivity](../topo_drawings/lab1-london-connectivity.png)

    You can now logout of the London VM 

    ```
    cisco@london-vm-00:~$ exit
    logout
    Connection to london-vm-00 closed.
    cisco@topology-host:~/LTRSPG-2212$ 
    ```


## Validate ISIS Topology

Our topology is running ISIS as its underlying IGP with basic settings pre-configured at startup in lab 1.

![ISIS Topology](../topo_drawings/isis-topology-medium.png)

For full size image see [LINK](../topo_drawings/isis-topology-large.png)


1. SSH into any router and verify that ISIS is up and running and all seven nodes are accounted for in the topology database


    ```
    show isis topology
    ```

    You should expect to see an entry for each xrd router 01 (London) -> 07 (Rome)
    ```
      RP/0/RP0/CPU0:london#show isis topology 
      Thu Jan  8 04:38:00.817 UTC

      IS-IS 100 paths to IPv4 Unicast (Level-1) routers
      System Id          Metric    Next-Hop           Interface       SNPA          
      london             --      

      IS-IS 100 paths to IPv4 Unicast (Level-2) routers
      System Id          Metric    Next-Hop           Interface       SNPA          
      london             --      
      amsterdam          1         amsterdam          Gi0/0/0/1       *PtoP*        
      berlin             2         amsterdam          Gi0/0/0/1       *PtoP*        
      zurich             2         paris              Gi0/0/0/2       *PtoP*        
      paris              1         paris              Gi0/0/0/2       *PtoP*        
      barcelona          2         paris              Gi0/0/0/2       *PtoP*        
      barcelona          2         amsterdam          Gi0/0/0/1       *PtoP*        
      rome               3         paris              Gi0/0/0/2       *PtoP*        
      rome               3         amsterdam          Gi0/0/0/1       *PtoP*        
      RP/0/RP0/CPU0:london#

    ```

    From London’s perspective, the IS-IS topology shows a pure Level-2 backbone design, with no active Level-1 adjacencies and full reachability achieved through L2 SPF computation. 
    Overall, the SPF results confirm a healthy, loop-free WAN core with consistent metrics and deterministic path selection, suitable for advanced traffic engineering mechanisms such as SRv6.


2. On **xrd01** validate end-to-end ISIS reachability by pinging **xrd07**:
   ```
   ping 10.0.0.7 source lo0
   ping fc00:0000:7777::1 source lo0
   ```

### Add Synthetic Latency to the Links

> [!NOTE]
> In a default containerized environment, direct XRd-to-XRd pings typically result in round-trip times of approximately 1–3 ms. To better approximate real-world WAN conditions, we intentionally move away from these values. As part of the lab setup, an Ansible playbook invokes a shell script that injects synthetic latency on the underlying Linux links, using the values shown in the diagram. These latencies are not meant to be realistic measurements, but rather a controlled mechanism to introduce deterministic path variation for later traffic engineering and path-selection exercises.
   
![WAN Latencies](../topo_drawings/lab1-latencies.png)


1. From a *topology-host* terminal session run the `add-latency.sh` script:
   ```
   ~/LTRSPG-2212/lab_1/add-latency.sh
   ```
   
## Validate BGP Peering

In the topology we are running a single ASN 65000 with BGP running on **xrd01**, **xrd05**, **xrd06**, **xrd07**.  Routers **xrd05** and **xrd06** are functioning as route reflectors and **xrd01** and **xrd07** are clients. 

![BGP Topology](../topo_drawings/bgp-topology-medium.png)

For full size image see [LINK](../topo_drawings/bgp-topology-large.png)

1. SSH into **London-xrd01** using the visual code extension and verify its neighbor state
    ```
    show ip bgp neighbors brief
    ```
    ```
      RP/0/RP0/CPU0:london#show ip bgp neighbors brief 
      Thu Jan  8 05:12:54.585 UTC

      Neighbor         Spk    AS  Description                         Up/Down  NBRState
      10.0.0.5          0 65000 iBGP to xrd05 RR                     01:13:08 Established 
      10.0.0.6          0 65000 iBGP to xrd06 RR                     01:13:09 Established 
      fc00:0:5555::1    0 65000 iBGPv6 to xrd05 RR                   01:13:10 Established 
      fc00:0:6666::1    0 65000 iBGPv6 to xrd06 RR                   01:13:05 Established 
      RP/0/RP0/CPU0:london#
    ``` 

2. Verify that router **london-xrd01** is advertising the attached ipv6 network ```fc00:0:1111::1/128``` 
    ```
    show bgp ipv6 unicast advertised summary
    ```

    ```
    RP/0/RP0/CPU0:london#show bgp ipv6 unicast advertised summary 
    Thu Jan  8 16:03:29.698 UTC
    Network            Next Hop        From            Advertised to
    fc00:0:1111::1/128 fc00:0:1111::1  Local           fc00:0:5555::1
                                       Local           fc00:0:6666::1

    Processed 1 prefixes, 2 paths
    RP/0/RP0/CPU0:london#
    ```

3. Verify that router **xrd01** has received route ```fc00:0:107:1::/64``` from the route reflectors **xrd05** and **xrd06**. Look for ```Paths: (2 available)```
    ```
    show bgp ipv6 unicast fc00:0:107:1::/64
    ```
    ```
    RP/0/RP0/CPU0:xrd01#show bgp ipv6 unicast fc00:0:107:1::/64
    Tue Jan 10 21:47:51.153 UTC
    BGP routing table entry for fc00:0:107:1::/64
    Versions:
    Process           bRIB/RIB  SendTblVer
    Speaker                  17           17
    Last Modified: Jan 10 21:46:29.402 for 00:01:21
    Paths: (2 available, best #1)
    Not advertised to any peer
    Path #1: Received by speaker 0
    Not advertised to any peer
    Local
        fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)              <------ origin from xrd07
        Origin IGP, metric 0, localpref 100, valid, internal, best, group-best
        Received Path ID 0, Local Path ID 1, version 17
        Originator: 10.0.0.7, Cluster list: 10.0.0.5                          <------ route reflector xrd05
    Path #2: Received by speaker 0
    Not advertised to any peer
    Local
        fc00:0:7777::1 (metric 3) from fc00:0:6666::1 (10.0.0.7)              <------ origin from xrd07
        Origin IGP, metric 0, localpref 100, valid, internal
        Received Path ID 0, Local Path ID 0, version 0
        Originator: 10.0.0.7, Cluster list: 10.0.0.6                          <------ route reflector xrd06
    ```

## Configure and Validate SRv6

In SRv6, the IPv6 destination address represents a set of one or more instructions. In our lab we will use SRv6 "micro segment" (SRv6 uSID or just "uSID" for short) instead of the full SRH. 

With SRv6 uSID:

 - The outer IPv6 destination address becomes the uSID carrier with the first 32-bits representing the uSID block, and the 6 remaining 16-bit chunks of the address become uSIDs or instructions
 - The existing ISIS and BGP Control Plane is leveraged without any change
 - The SRH can be used if our uSID instruction set extends beyond the 6 available in the outer IPv6 destination address
 - SRv6 uSID is based on the Compressed SRv6 Segment List Encoding in [RFC 9080](https://datatracker.ietf.org/doc/rfc9800/)

For reference one of the most recent IOS-XR Configuration guides for SR/SRv6 and ISIS can be found here: [LINK](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/segment-routing/24xx/configuration/guide/b-segment-routing-cg-cisco8000-24xx/configuring-segment-routing-over-ipv6-srv6-micro-sids.html)

SRv6 uSID locator and source address information for nodes in the lab:

| Router Name | Loopback Int|    Locator Prefix    |  Source-address     |                                           
|:------------|:-----------:|:--------------------:|:--------------------:|                          
| london-xrd01     | loopback 0  | fc00:0000:1111::/48  | fc00:0000:1111::1    |
| amsterdam-xrd02  | loopback 0  | fc00:0000:2222::/48  | fc00:0000:2222::1    |
| berlin-xrd03     | loopback 0  | fc00:0000:3333::/48  | fc00:0000:3333::1    |
| zurich-xrd04     | loopback 0  | fc00:0000:4444::/48  | fc00:0000:4444::1    |
| paris-xrd05      | loopback 0  | fc00:0000:5555::/48  | fc00:0000:5555::1    |
| barcelona-xrd06  | loopback 0  | fc00:0000:6666::/48  | fc00:0000:6666::1    |
| rome-xrd07       | loopback 0  | fc00:0000:7777::/48  | fc00:0000:7777::1    |


> [!NOTE]
> We've preconfigured SRv6 on **xrd02** thru **xrd06**, so you'll only need to configure **xrd01** and **xrd07**

### Configure SRv6 on xrd01
1. SSH to **xrd01** and enable SRv6 globally and define SRv6 locator and source address for outbound encapsulation 


    ```
    conf t

    segment-routing
      srv6
        encapsulation
          source-address fc00:0000:1111::1
        locators
          locator MyLocator
            micro-segment behavior unode psp-usd
            prefix fc00:0000:1111::/48
       commit
    ```

2. Enable SRv6 for ISIS  
    ```
    router isis 100
      address-family ipv6 unicast
         segment-routing srv6
           locator MyLocator
       commit
    ```

3. Enable SRv6 for BGP 
    ```
    router bgp 65000
    address-family ipv4 unicast
      segment-routing srv6
      locator MyLocator
      !
    ! 
    address-family ipv6 unicast
      segment-routing srv6
      locator MyLocator
      !
    !
    neighbor-group xrd-ipv4-peer
      address-family ipv4 unicast
      !
    ! 
    neighbor-group xrd-ipv6-peer
      address-family ipv6 unicast
      !
    !
    commit
    ```

### Configure SRv6 on xrd07


1. Using the Visual Code extension ssh to **xrd07** and apply the below config in a single shot:

![ssh into xrd07](../topo_drawings/lab1-ssh-xrd07.png)


```
    conf t

    router isis 100
     address-family ipv6 unicast
     segment-routing srv6
     locator MyLocator
     !
    !
    router bgp 65000
     address-family ipv4 unicast
     segment-routing srv6
     locator MyLocator
     !
    ! 
    address-family ipv6 unicast
     segment-routing srv6
     locator MyLocator
     !
    !
    neighbor-group xrd-ipv4-peer
     address-family ipv4 unicast
     !
    ! 
    neighbor-group xrd-ipv6-peer
     address-family ipv6 unicast
     !
    !
    segment-routing
     srv6
     encapsulation
     source-address fc00:0000:7777::1
    !
     locators
      locator MyLocator
       micro-segment behavior unode psp-usd
       prefix fc00:0000:7777::/48
      !
    !
    commit
```

### Validate SRv6 configuration and reachability

1. On **xrd01** run validation commands
    ```
    show segment-routing srv6 sid
    ```
    ```diff
    RP/0/RP0/CPU0:xrd01#show segment-routing srv6 sid
    Fri Dec 15 22:37:40.028 UTC

    *** Locator: 'MyLocator' *** 

    SID                         Behavior          Context                           Owner               State  RW
    --------------------------  ----------------  --------------------------------  ------------------  -----  --
    fc00:0:1111::               uN (PSP/USD)      'default':4369                    sidmgr              InUse  Y 
    fc00:0:1111:e000::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
    fc00:0:1111:e001::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
    fc00:0:1111:e002::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
    fc00:0:1111:e003::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 
    +fc00:0:1111:e004::         uDT4              'default'                         bgp-65000           InUse  Y 
    +fc00:0:1111:e005::         uDT6              'default'                         bgp-65000           InUse  Y
    ```
> [!NOTE]
> The bottom two entries. These SIDs belong to BGP and represent End.DT behaviors. Any packet arriving with either of these SIDs as the outer IPv6 destination address will be decapsulated and then an LPM lookup in the global/default routing table will be performed on the inner destination address. 

2. Validate the SRv6 prefix-SID configuration. As example for **xrd01** look for *SID value: fc00:0000:1111::*
    ```
    show isis segment-routing srv6 locator detail 
    ```

    ```diff
    RP/0/RP0/CPU0:xrd01#show isis segment-routing srv6 locators detail 

    IS-IS 100 SRv6 Locators
    Name                  ID       Algo  Prefix                    Status
    ------                ----     ----  ------                    ------
    MyLocator             1        0     fc00:0000:1111::/48       Active
    Advertised Level: level-1-2   
    Level: level-1      Metric: 1        Administrative Tag: 0         
    Level: level-2-only Metric: 1        Administrative Tag: 0         
    SID behavior: uN (PSP/USD)
    +SID value:    fc00:0000:1111::                      <------------ HERE
    Block Length: 32, Node Length: 16, Func Length: 0, Args Length: 80
    ```

## End-to-End Connectivity - Edgeshark


EdgeShark is a browser-based packet capture and analysis tool built into Containerlab. Key features of Edgeshark for our lab.
* Support for Docker containers
* Integrated with Visual Studio Code through Containerlab extensions
* Within Visual Studio Code you can highlight an XRd router link and launch directly

We will use this tool within the labs to allow the students to see actual SRv6 packets on the wire.

To launch EdgeShark and inspect traffic, simply click on the interface you want to capture packets from in the Containerlab tab within Visual Studio Code. In this case, we want to capture traffic on interface Gi0/0/0/0 of *xrd01*.

![Edgeshark launch](../topo_drawings/lab1-edgeshark-launch.png)

Clicking on the interface will automatically launch wireshark and starts the capture.

## End of Lab 1

Lab 1 is completed, you can either: 
  - Perform the optional [Lab 1 packet walk](https://github.com/cisco-asp-web/LTRSPG-2212/blob/main/lab_1/lab_1-packet-walk.md)
  - Proceed to [Lab 2](https://github.com/cisco-asp-web/LTRSPG-2212/blob/main/lab_2/lab_2-guide.md)
