# Lab 4: SRv6 on SONiC [20 Min]

### Description
From the SONiC homepage: https://sonicfoundation.dev/

*Software for Open Networking in the Cloud (SONiC) is an open source network operating system (NOS) based on Linux that runs on switches from multiple vendors and ASICs. SONiC offers a full suite of network functionality, like BGP and RDMA, that has been production-hardened in the data centers of some of the largest cloud service providers. It offers teams the flexibility to create the network solutions they need while leveraging the collective strength of a large ecosystem and community.*
 
In lab 4 we'll work with our small SONiC CLOS topology; we'll explore the SONiC/Linux and FRR CLIs, and we'll use Ansible scripts to configure interfaces, BGP, and finally SRv6.

## Contents
- [Lab 4: SRv6 on SONiC \[20 Min\]](#lab-4-srv6-on-sonic-20-min)
    - [Description](#description)
  - [Contents](#contents)
  - [Lab Objectives](#lab-objectives)
  - [Containerlab SONiC topology](#containerlab-sonic-topology)
  - [SONiC: A Very Quick Tour](#sonic-a-very-quick-tour)
    - [SONiC Docker Containers](#sonic-docker-containers)
  - [SONiC Configuration Files](#sonic-configuration-files)
    - [config load, config reload, \& config save](#config-load-config-reload--config-save)
    - [Configure leaf00 from SONiC CLI](#configure-leaf00-from-sonic-cli)
  - [Fabric Config Automation with Ansible](#fabric-config-automation-with-ansible)
    - [Verify SONiC BGP peering](#verify-sonic-bgp-peering)
    - [SONiC SRv6 configuration](#sonic-srv6-configuration)
    - [Verify London VM backend network reachability](#verify-london-vm-backend-network-reachability)
  - [End of lab 4](#end-of-lab-4)

## Lab Objectives
We will have achieved the following objectives upon completion of Lab 4:

* Understanding of SONiC's architecture and configuration
* Understanding of SONiC FRR/BGP
* Understanding of SONiC's SRv6 configuration and capabilities


## Containerlab SONiC topology

In lab 1 our containerlab script deployed both the XRd topology and the SONiC nodes in our London AI/ML backend data center. 

Our SONiC ML Training Fabric topology looks like this:

<img src="../topo_drawings/lab4-topology-diagram.png" width="800" />

## SONiC: A Very Quick Tour

SONiC is Linux plus a microservices-style architecture with modules running as Docker containers. The containers interact and communicate with each other through the Switch State Service (*`swss`*) container. The infrastructure also relies on the use of a *redis-database* engine: a key-value database to provide a language independent interface, a method for data persistence, replication, and multi-process communication among all SONiC subsystems.

For a deep dive on SONiC architecture and containers please see: https://sonicfoundation.dev/deep-dive-into-sonic-architecture-design/


1. ssh to **leaf00** in our topology using the visual code extension
  
  > [!NOTE]
  >user/password is **admin/admin**)

   ```
   ssh admin@clab-cleu26-sonic-leaf-00
   ```

2. List SONiC's docker containers.
    ```
    docker ps
    ```

    Expected output:
    ```
    admin@sonic:~$ docker ps
    CONTAINER ID  IMAGE                              COMMAND                CREATED        STATUS       PORTS  NAMES
    fd325f9f71a3  docker-snmp:latest                 "/usr/bin/docker-snm…" 4 minutes ago  Up 4 minutes        snmp
    83abaaeb0eda  docker-platform-monitor:latest     "/usr/bin/docker_ini…" 4 minutes ago  Up 4 minutes        pmon
    07b16407200a  docker-sonic-mgmt-framework:latest "/usr/local/bin/supe…" 4 minutes ago  Up 4 minutes        mgmt-framework
    e92cfef2d1a7  docker-lldp:latest                 "/usr/bin/docker-lld…" 4 minutes ago  Up 4 minutes        lldp
    e039e0c50696  docker-sonic-gnmi:latest           "/usr/local/bin/supe…" 4 minutes ago  Up 4 minutes        gnmi
    0eb9d4243f43  docker-router-advertiser:latest    "/usr/bin/docker-ini…" 6 minutes ago  Up 6 minutes        radv
    a802d70ada48  docker-fpm-frr:latest              "/usr/bin/docker_ini…" 6 minutes ago  Up 6 minutes        bgp
    c6bd49fba18d  docker-syncd-vpp:latest            "/usr/local/bin/supe…" 6 minutes ago  Up 6 minutes        syncd
    81ea6a8d2eba  docker-teamd:latest                "/usr/local/bin/supe…" 6 minutes ago  Up 6 minutes        teamd
    98c4bb45296b  docker-orchagent:latest            "/usr/bin/docker-ini…" 6 minutes ago  Up 6 minutes        swss
    5459d7bc624a  docker-eventd:latest               "/usr/local/bin/supe…" 6 minutes ago  Up 6 minutes        eventd
    bab374f5a2b5  docker-database:latest             "/usr/local/bin/dock…" 6 minutes ago  Up 6 minutes        database
    ```

  ### SONiC Docker Containers

| Docker Container Name| Description                                                      |
|:---------------------|:-----------------------------------------------------------------|
| BGP                  | Runs FRR [Free Range Routing](https://frrouting.org/) |
| Database             | Hosts the redis-database engine|
| LLDP                 | Hosts LLDP. Includes 3 process *llpd*, *LLDP-syncd*, *LLDPmgr* |
| MGMT-Framework       | North Bound Interfaces (NBIs) for  managing configuration and status|
| PMON                 | Runs *sensord* daemon used to log and alert sensor data |
| RADV                 | Hosts *radv* daemon and handles IPv6 router solicitations / router advertisements |
| SNMP                 | Hosts SNMP feature. *SNMPD* and *SNMP-Agent* |
| SWSS                 | Collection of tools to allow communication among all SONiC modules |
| SYNCD                | Synchronization of the switch's network state with the switch's actual hardware/ASIC |
| TeamD                | Runs open-source implementation of LAG protocol |
| GNMI                 | SONiC gnmi/telemetry service |

> [!NOTE]
> **Control Plane**: SONiC leverages the open-source [Free Range Routing](https://frrouting.org/) (FRR) routing stack for its Control Plane. Currently the only supported routing protocol is BGP, however, FRR supports ISIS and OSPF, so in the future we could see SONiC incorporating those protocols as well.
> 
> The *docker ps* output above included a container named **bgp**. In reality this is FRR running as a container.

In addition to normal Linux CLI, SONiC has its own CLI that operates from the Linux shell:

3. Try some SONiC CLI commands:
    ```
    show ?
    show interface status
    show ip interfaces
    show ipv6 interfaces
    show version
    ```
    If you would like to explore more we've included a short [SONiC CLI command reference](https://github.com/cisco-asp-web/LTRSPG-2212/blob/main/lab_4/sonic_cli_reference.md)

5. Access **leaf00's** FRR/BGP container via *vtysh*
    ```
    vtysh
    ```

    Expected output:
    ```
    admin@sonic:~$ vtysh

    Hello, this is FRRouting (version 10.0.1).
    Copyright 1996-2005 Kunihiro Ishiguro, et al.

    2025/05/04 21:01:06 [YDG3W-JND95] FD Limit set: 1048576 is stupidly large.  Is this what you intended?  Consider using --limit-fds also limiting size to 100000
    sonic# 
    ```

6. FRR looks a whole lot like classic IOS:
    ```
    show run
    show interface brief
    exit
    ```

## SONiC Configuration Files
Configuration state in SONiC is saved in two separate files. The first is the **/etc/sonic/config_db.json** file, which contains global configuration attributes such as hostname, interfaces, IP addresses, etc. The second is the FRR control plane configuration at **/etc/sonic/frr/bgpd.conf**.

### config load, config reload, & config save

**config load**

The command *config load* is used to load a configuration from an input file; the default is */etc/sonic/config_db.json*, unless specified otherwise. This command does not flush the config DB before loading the new configuration, rather it performs a *diff* on the existing and applies the new. 

- Usage:
```
config load [-y|--yes] [<filename>]
```
- Example:
```
admin@sonic::~$ sudo config load
Load config from the file /etc/sonic/config_db.json? [y/N]: y
Running command: /usr/local/bin/sonic-cfggen -j /etc/sonic/config_db.json --write-to-db
```

**config save**

*config save* is used to save the redis CONFIG_DB into the user-specified filename or into the default /*etc/sonic/config_db.json*. This is analogous to the Cisco IOS command *copy run start*. 

- Usage:
```
config save [-y|--yes] [<filename>]
```
- Example (Save configuration to /etc/sonic/config_db.json):

```
admin@sonic::~$ sudo config save -y
```

- Example (Save configuration to a specified file):
```
admin@sonic::~$ sudo config save -y /etc/sonic/config2.json
```

**View the configuration through SONiC CLI**

As network engineers, we still like to see the traditionnal "show run" on our devices. On SONiC, the *show runningconfiguration* command displays the current active configuration of various system components. You can view specific elements such as BGP, interfaces, ports, or the full configuration using subcommands like *show runningconfiguration all*. This is useful for verifying what is currently applied without needing to inspect config files directly.

```
admin@sonic:~$ show runningconfiguration all
{
    "AUTO_TECHSUPPORT": {
        "GLOBAL": {
            "available_mem_threshold": "10.0",
            "max_core_limit": "5.0",
            "max_techsupport_limit": "10.0",
            "min_available_mem": "200",
            "rate_limit_interval": "180",
            "since": "2 days ago",
            "state": "enabled"
        }
    },
    "AUTO_TECHSUPPORT_FEATURE": {
        "bgp": {
            "available_mem_threshold": "10.0",
            "rate_limit_interval": "600",
            "state": "enabled"
        },
```

**Edit configuration through SONiC CLI**

The SONiC CLI can also be used to apply non-control plane configurations. From the Linux shell enter *config* and the command syntax needed. 

```
admin@sonic::~$ config ?
Usage: config [OPTIONS] COMMAND [ARGS]...

  SONiC command line - 'config' command
```

### Configure leaf00 from SONiC CLI

Before we proceed with applying full fabric configurations via Ansible, we wanted to demonstrate SONiC CLI by manually configuring **leaf00's** hostname and Loopback0 ip addresses


1. Using the containerlab visual code extension, ssh to **leaf00** (password is `admin`) and configure hostname and *Loopback0* IPv4 and IPv6 addresses
   ```
   sudo config hostname leaf00
   sudo config interface ip add Loopback0 10.0.0.4/32
   sudo config interface ip add Loopback0 fc00:0:1004::1/128
   ```

> [!NOTE]
> Logout and log back in to *leaf00* to see the hostname change take effect

Our SONiC fabric will use IPv6 link local addresses for the BGP underlay, so we only need to configure IPv6 addresses for the London VM facing interface Ethernet16. Note: the backend network will be IPv6 only.

3. Configure interface Ethernet16 IPv6 address
   ```
   sudo config interface ip add Ethernet16 fcbb:0:800::1/64
   ```

4. Save configuration
   ```
   sudo config save -y
   ```
   
5. Exit the sonic node and ssh back in to see the hostname change in effect

6. Do a quick verification of interface IP:
   ```
   show ip interfaces 
   show ipv6 interfaces
   ```

   Example truncated output:
   ```diff
   admin@leaf00:~$ show ipv6 interfaces
   Interface    Master    IPv6 address/mask                        Admin/Oper    BGP Neighbor    Neighbor IP
   -----------  --------  ---------------------------------------  ------------  --------------  -------------
    Ethernet0              fe80::203d:a9ff:fe5d:83c6%Ethernet0/64   up/up         N/A             N/A
    Ethernet4              fe80::203d:a9ff:fe5d:83c6%Ethernet4/64   up/up         N/A             N/A
    Ethernet8              fe80::203d:a9ff:fe5d:83c6%Ethernet8/64   up/up         N/A             N/A
    Ethernet12             fe80::203d:a9ff:fe5d:83c6%Ethernet12/64  up/up         N/A             N/A
   +Ethernet16             fcbb:0:800::1/64                         up/up         N/A             N/A
                           fe80::203d:a9ff:fe5d:83c6%Ethernet16/64                N/A             N/A
   +Loopback0              fc00:0:1004::1/128                       up/up         N/A             N/A
   ```


## Fabric Config Automation with Ansible 

We'll use Ansible and execute the [sonic-playbook.yaml](https://github.com/cisco-asp-web/LTRSPG-2212/blob/main/lab_4/ansible/sonic-playbook.yaml) to complete the configuration of our SONiC fabric. This playbook performs a number of tasks including:

* Copy each node's *config_db.json* file to the */etc/sonic/* directory [Example spine00 config_db.json](https://github.com/cisco-asp-web/LTRSPG-2212/blob/main/lab_4/sonic-config/spine00/config_db.json)
* Load the config to activate the new settings
* Copy over and run a loopback shell script that we've created for each node [Example spine00 loopback.sh](https://github.com/cisco-asp-web/LTRSPG-2212/blob/main/lab_4/sonic-config/spine00/loopback.sh)
* Save the config
* Create and activate a loopback interface called **sr0** on each node. This loopback is needed for SONiC SRv6 functionality
* Copy and load FRR configs, which include BGP and SRv6 attributes, to each node; [Example spine00 frr.conf](https://github.com/cisco-asp-web/LTRSPG-2212/blob/main/lab_4/sonic-config/spine00/frr.conf)


1. Launch a terminal on the *`topology host`* using the visual code containerlab extension:

<img src="../topo_drawings/lab4-terminal.png" width="800" />

2. cd into the lab_4 directory and execute the *sonic-playbook.yaml*
    ```
    cd ~/LTRSPG-2212/lab_4/ansible
    ansible-playbook -i hosts sonic-playbook.yaml -e "ansible_user=admin ansible_ssh_pass=admin ansible_sudo_pass=admin" -vv
    ```

> [!Note] 
> The sonic playbook produces a lot of console output. By the time the playbook completes we expect to see something like this:

```
    PLAY RECAP *************************************************************************************
    leaf00   : ok=20   changed=15   unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
    leaf01   : ok=20   changed=15   unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
    leaf02   : ok=20   changed=15   unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
    spine00  : ok=18   changed=14   unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
    spine01  : ok=18   changed=14   unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
    spine02  : ok=18   changed=14   unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
``` 

**Verify Configuration of FRR in Leaf00**

FRR operates in SONiC very similar to Classic IOS commands. 

1. Return to your **leaf** terminal session and invoke FRR's VTY shell
   ```
   vtysh
   ```

2. Show the running FRR config
   ```
   show run
   ```

   We expect to see BGP configurations with unnumbered peering over EthernetX interfaces and SRv6 config including locator, source address for encapsulation, and some static uSID entries.

### Verify SONiC BGP peering

With our backend DC fabric now configured we will check to make sure that BGP peering was established. Use the below diagram as a reference to the ASN configured in the prior steps.

<img src="../topo_drawings/lab4-fabric-asn-topology.png" width="800" />

1. Using the visual code containerlab extension, ssh to one or more SONiC nodes and spot check BGP peering . You can SSH into any SONiC container.  (user: admin, pw: admin)

   <img src="../topo_drawings/lab4-ssh-sonic.png" width="400" />

    ```
    vtysh
    ```
    ```
    show bgp summary
    ```
    Expected output from leaf00:
    ```
    leaf00# show bgp summary 

    IPv6 Unicast Summary:
    BGP router identifier 10.0.0.200, local AS number 65200 VRF default vrf-id 0
    BGP table version 58
    RIB entries 47, using 6016 bytes of memory
    Peers 4, using 80 KiB of memory

    Neighbor     V       AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd  PfxSnt Desc
    Ethernet0    4    65000        54        40       58    0    0 00:14:43          12       15 N/A
    Ethernet4    4    65001        99        36       58    0    0 00:14:41          12       15 N/A
    Ethernet8    4    65002        63        36       58    0    0 00:14:41          12       15 N/A

    Total number of neighbors 3
    ```
    
### SONiC SRv6 configuration

Our SONiC topology has now been configured for SRv6 uSID forwarding with each node assigned SRv6 locators as shown in the diagram:

<img src="../topo_drawings/lab4-topology-with-locators.png" width="800" />

If your *vtysh* session is on **leaf00** keep it open. If not, ssh to **leaf00** using the visual code containerlab extension and invoke vtysh for the next few tasks:


1. Check SONiC SRv6 configuration on **leaf00**
   ```
   show run
   ```

   Example SRv6 config output:
   ```diff
   segment-routing
    srv6
      static-sids
   +   sid fc00:0:1004::/48 locator MAIN behavior uN                      <-- Locator behavior "uN"
   +   sid fc00:0:1004:fe04::/64 locator MAIN behavior uDT4 vrf default   <-- static uDT4 function for prefixes in the default ipv4 table
   +   sid fc00:0:1004:fe06::/64 locator MAIN behavior uDT6 vrf default   <-- static uDT6 function for prefixes in the default ipv6 table    
      exit
      !
    exit
    !
    srv6
      encapsulation
      source-address fc00:0:1004::1
      locators
      locator MAIN
        prefix fc00:0:1004::/48 block-len 32 node-len 16 func-bits 16
        behavior usid
      exit
      !
      exit
      !
      formats
      format usid-f3216
      exit
      !
      format uncompressed-f4024
      exit
    ```

2. Check locator/sid-manager status 
    ```
    show segment-routing srv6 locator 
    show segment-routing srv6 manager
    ```

    Expected output:
    ```
    leaf00# show segment-routing srv6 locator 
    Locator:
    Name                 ID      Prefix                   Status
    -------------------- ------- ------------------------ -------
    MAIN                       1 fc00:0:1004::/48         Up

    leaf00# show segment-routing srv6 manager 
    Parameters:
      Encapsulation:
        Source Address:
          Configured: fc00:0:1004::1
    ```

3. Compare an FRR BGP route entry and its corresponding Linux route entry:

    From the FRR vtysh session:
    ```
    show bgp ipv6 uni fcbb:0:800:2::/64
    ```

    Expected output:
    ```diff
    leaf00# show bgp ipv6 uni fcbb:0:800:2::/64
    BGP routing table entry for fcbb:0:800:2::/64, version 27
    +Paths: (3 available, best #1, table default)
      Advertised to non peer-group peers:
      Ethernet0 Ethernet4 Ethernet8 Ethernet12
    + 65000 65202
        fe80::20a3:c7ff:fe5e:5c58 from Ethernet0 (10.0.0.0)
        (fe80::20a3:c7ff:fe5e:5c58) (prefer-global)
          Origin IGP, valid, external, multipath, best (Older Path)
          Last update: Sun Jun  1 03:17:37 2025
    + 65001 65202
        fe80::20dc:72ff:fe50:c026 from Ethernet4 (10.0.0.1)
        (fe80::20dc:72ff:fe50:c026) (prefer-global)
          Origin IGP, valid, external, multipath
          Last update: Sun Jun  1 03:17:38 2025
    + 65002 65202
        fe80::20c8:3aff:fed9:1a10 from Ethernet8 (10.0.0.2)
        (fe80::20c8:3aff:fed9:1a10) (prefer-global)
          Origin IGP, valid, external, multipath
          Last update: Sun Jun  1 03:17:38 2025
    ```

    FRR's BGP show command output again resembles IOS output. The prefix is known via **leaf00's** 3 BGP unnumbered neighbors.

    Exit vtysh and check the same route in the Linux table:
    ```
    exit
    ```
    ```
    ip -6 route show fcbb:0:800:2::/64
    ```

    Example output:
    ```diff
    $ ip -6 route show fcbb:0:800:2::/64
    +fcbb:0:800:2::/64 nhid 81 proto bgp src fc00:0:1004::1 metric 20 pref medium
	   nexthop via fe80::20a3:c7ff:fe5e:5c58 dev Ethernet0 weight 1 
	   nexthop via fe80::20dc:72ff:fe50:c026 dev Ethernet4 weight 1 
	   nexthop via fe80::20c8:3aff:fed9:1a10 dev Ethernet8 weight 1 
    ```

    Note how the entry has the notation *`proto bgp src`* which indicates the route was learned from BGP. The route also has 3 ECMP paths via the BGP unnumbered / IPv6 link-local sessions.


### Verify London VM backend network reachability

1. SSH to the **london-vm-00** from the **topology-host**
   
    ```
    ssh london-vm-00
    ```
    
2. Disply the VM's ipv6 routing table:
   
    ```
    ip -6 route 
    ```

    Or to see *`Backend`* specific routes:
    ```
    ip -6 route | grep ens5
    ```

    Expected output:
    ```
    $ ip -6 route | grep ens5
    fcbb:0:800::/64 dev ens5 proto kernel metric 256 pref medium
    fcbb::/32 via fcbb:0:800::1 dev ens5 proto static metric 1024 pref medium
    fe80::/64 dev ens5 proto kernel metric 256 pref medium
    ```

3. Ping **london-vm-01** and **london-vm-02** over the *`Backend/SONiC`* network:

    ```
    ping fcbb:0:800:1::2 -i .3 -c 3
    ```

    ```
    admin@leaf00:~$ ping fcbb:0:800:1::2 -i .3 -c 3
    PING fcbb:0:800:1::2(fcbb:0:800:1::2) 56 data bytes
    64 bytes from fcbb:0:800:1::2: icmp_seq=1 ttl=62 time=2.13 ms
    64 bytes from fcbb:0:800:1::2: icmp_seq=2 ttl=62 time=1.74 ms
    64 bytes from fcbb:0:800:1::2: icmp_seq=3 ttl=62 time=2.09 ms

    --- fcbb:0:800:1::2 ping statistics ---
    3 packets transmitted, 3 received, 0% packet loss, time 602ms
    rtt min/avg/max/mdev = 1.744/1.988/2.131/0.173 ms
    ```

    
## End of lab 4
Please proceed to [Lab 5: Host Based SRv6 and SRv6 for AI Backend Networks](https://github.com/cisco-asp-web/LTRSPG-2212/blob/main/lab_5/lab_5-guide.md)

