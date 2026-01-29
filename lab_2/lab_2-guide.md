# Lab 2: Configure SRv6 L3VPN and SRv6-TE [20 Min]

### Description
In Lab 2 we will establish an SRv6 Layer-3 VPN named *`carrots`*.  The *carrots* vrf will include the *London "storage"* and *Rome* containers connected to **london-xrd01** and **rome-xrd07**.  

Once the L3VPN is established we will then setup SRv6-TE traffic steering from *London* such that traffic to *Rome* prefix 40.0.0.0/24 will take a different path than traffic to Rome prefix 50.0.0.0/24.

## Contents
- [Lab 2: Configure SRv6 L3VPN and SRv6-TE \[20 Min\]](#lab-2-configure-srv6-l3vpn-and-srv6-te-20-min)
    - [Description](#description)
  - [Contents](#contents)
  - [Lab Objectives](#lab-objectives)
  - [Topology](#topology)
  - [Configure SRv6 L3VPN](#configure-srv6-l3vpn)
    - [Configure SRv6 L3VPN on rome-xrd07](#configure-srv6-l3vpn-on-rome-xrd07)
  - [Configure SRv6-TE steering for L3VPN](#configure-srv6-te-steering-for-l3vpn)
    - [Create SRv6-TE steering policy](#create-srv6-te-steering-policy)
    - [Validate SRv6-TE steering of L3VPN traffic](#validate-srv6-te-steering-of-l3vpn-traffic)
  - [End of Lab 2](#end-of-lab-2)

## Lab Objectives
We will have achieved the following objectives upon completion of Lab 2:

* Configure and validate SRv6 L3VPN
* Configuration and testing of SRv6 TE policy and traffic steering

## Topology
![L3VPN Topology](/topo_drawings/lab2-l3vpn-carrots.png)


## Configure SRv6 L3VPN
The SRv6-based IPv4/IPv6 L3VPN featureset enables operation of IPv4/IPv6 L3VPN over a SRv6 data plane. Traditionally L3VPN has been operated over MPLS or SR-MPLS. SRv6 L3VPN uses the locator/function aspect of SRv6 Segment IDs (SIDs) instead of PE + VPN labels. 

Example: 

|     Locator    | Function |                                         
|:---------------|:--------:|
| fc00:0000:7777:|   e004:: |


In this lab a BGP L3VPN SID will be allocated in per-VRF mode and provides End.DT4 or End.DT6 functionality. End.DT4/6 represents the Endpoint with decapsulation and IPv4 or v6 lookup in a specific VRF table.

For more details on SRv6 network programming Endpoint Behavior functionality please see RFC 8986 [LINK](https://datatracker.ietf.org/doc/html/rfc8986#name-enddt6-decapsulation-and-sp)

BGP encodes the SRv6 SID in the prefix-SID attribute of the IPv4/6 L3VPN Network Layer Reachability Information (NLRI) and advertises it via it's MP-BGP peers. The Ingress PE (provider edge) router encapsulates the VRF IPv4/6 traffic with the SRv6 VPN SID and sends it over the SRv6 network.

The *carrots* VRFs is setup on the two edge routers in our SP network: **london-xrd01** and **rome-xrd07**. Intermediate routers do not need to be VRF aware and are instead forwarding on the SRv6 data plane. *(technically the intermediate routers don't need to be SRv6 aware and could simply perform IPv6 forwarding based on the outer IPv6 header)*.  

The VRF instances and their interfaces have been preconfigured, allowing us to focus on the SRv6 BGP configuration. 

Optional: if you wish to see the existing VRF configuration run these commands on *rome-xrd07*:
```
show run vrf
show run interface GigabitEthernet 0/0/0/0
```

### Configure SRv6 L3VPN on rome-xrd07

We'll start with **rome-xrd07** as it will need a pair of static routes for reachability to the  **Rome container's** "40" and "50" network prefixes (loopback interfaces). Later we'll create SRv6-TE steering policies for traffic to the "40" and "50" prefixes:  

> [!NOTE]
> All of the below commands are also available in the *`quick config doc.`*. Be aware that the quick config document contains both the L3VPN configuration as well as the L3VPN TE configuration. [HERE](https://github.com/cisco-asp-web/LTRSPG-2212/blob/main/lab_2/lab_2_quick_config.md) 

   
1. **rome-xrd07** vrf static route configuration
   
   SSH into rome-xrd07 and copy/paste the static route config below the image:

   **rome-xrd07**
   ```yaml
      conf t
      
      router static
        vrf carrots
          address-family ipv4 unicast
            40.0.0.0/24 10.107.1.2
            50.0.0.0/24 10.107.1.2
          commit
    ```
2. Verify **Rome** VRF prefix reachability  
    Ping check from Rome-xrd07 gi 0/0/0/0 to Rome's Container NIC:  
    ```
    ping vrf carrots 10.107.1.1
    ping vrf carrots 40.0.0.1
    ping vrf carrots 50.0.0.1
    ping vrf carrots fc00:0:107:1::2
    ```

3. Enable BGP L3VPN on **rome-xrd07**
   
     The *carrots* L3VPN is dual-stack so we will be adding both vpnv4 and vpnv6 address-families to the BGP neighbor-group for ipv6 peers. For example you will enable L3VPN in the neighbor-group template by issuing the *address-family vpnv4/6 unicast* command. 

    **Rome-xrd07**
    ```yaml
    conf t
    router bgp 65000
      neighbor-group xrd-ipv6-peer
        address-family vpnv4 unicast
        next-hop-self

        address-family vpnv6 unicast
        next-hop-self
      commit
    ```

4. Enable SRv6 for VRF carrots and redistribute connected/static
   
    Next we add VRF *carrots* into BGP and enable SRv6 to the IPv4 and IPv6 address family with the command *`segment-routing srv6`*. In addition we will tie the VRF to the SRv6 locator *`MyLocator`* configured in Lab 1.

    On **rome-xrd07** we will need to redistribute both the connected and static routes to provide reachability to Rome and its additional prefixes. Therefore, we will add *`redistribute static`* for VRF *carrots*.

    **rome-xrd07**  
    ```yaml
    conf t
    router bgp 65000
      vrf carrots
        rd auto
        address-family ipv4 unicast
          segment-routing srv6
          locator MyLocator
          alloc mode per-vrf
          redistribute static
          redistribute connected
      
        address-family ipv6 unicast
          segment-routing srv6
          locator MyLocator
          alloc mode per-vrf
          redistribute static
          redistribute connected
      commit
      ```
### Configure SRv6 L3VPN on xrd01 and RR xrd05

1. Using the visual code extension, ssh to **london-xrd01** and apply the configuration in a single step:

    ```yaml
    conf t

    router bgp 65000
    neighbor-group xrd-ipv6-peer
      address-family vpnv4 unicast
      next-hop-self
      
      address-family vpnv6 unicast
      next-hop-self
      
    vrf carrots
      rd auto
      address-family ipv4 unicast
      segment-routing srv6
        locator MyLocator
        alloc mode per-vrf
      redistribute connected
      
      address-family ipv6 unicast
      segment-routing srv6
        locator MyLocator
        alloc mode per-vrf
      redistribute connected
    commit
    ```

2. Configure Route Reflector **paris-xrd05**  
   
    The BGP route reflectors will also need to have L3VPN capability added to their peering group. **barcelona-xrd06** has been preconfigured, so you only need to configure **paris-xrd05**
   
     Using the visual code extension, ssh to **paris-xrd05** and apply the configuration in a single step:

    ```yaml
    conf t
    router bgp 65000
    neighbor-group xrd-ipv6-peer
      address-family vpnv4 unicast
      route-reflector-client
      
      address-family vpnv6 unicast
      route-reflector-client
    commit
    ```

### Validate SRv6 L3VPN

Validation command output examples can be found at this [LINK](/lab_2/validation-cmd-output.md)
> [!NOTE]
> It can take a few seconds after configuration before you see routes populate through the network and be visible in the routing tables.

> [!IMPORTANT]
> **london-xrd01** and **rome-xrd07** are configured to use dynamic RD allocation, so the L3VPN RD+prefix combination shown in the lab guide may differ from the one you see in your environment. For example, **rome-xrd07** might advertise the 40.0.0.0/24 prefix with rd 10.0.0.7:0 or it might be rd 10.0.0.7:1
> 
1. From **london-xrd01** run the following set of validation commands (for the sake of time you can paste them in as a group, or spot check some subset of commands). Again be aware the rd value may differ then those in the below commands:
   ```
   show segment-routing srv6 sid
   show bgp vpnv4 unicast
   show bgp vpnv4 unicast rd 10.0.0.7:1 40.0.0.0/24
   show bgp vpnv6 unicast
   ping vrf carrots 40.0.0.1
   ping vrf carrots 50.0.0.1
   ```
   
   Example validation for vpnv4 route
   ```diff
   RP/0/RP0/CPU0:xrd01#show bgp vpnv4 unicast rd 10.0.0.7:1 40.0.0.0/24   
   Tue Jan 31 23:36:41.390 UTC
   +BGP routing table entry for 40.0.0.0/24, Route Distinguisher: 10.0.0.7:1   <--- WE HAVE A ROUTE. YAH
   Versions:
     Process           bRIB/RIB  SendTblVer
     Speaker                  11           11
     Last Modified: Jan 31 23:34:44.948 for 00:01:56
     Paths: (2 available, best #1)
       Not advertised to any peer
     Path #1: Received by speaker 0
     Not advertised to any peer
     Local
   +    fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)   <--------- SOURCE xrd07
   +      Received Label 0xe0040     <-------- SRv6 Function "e004"
         Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, not-in-vrf
         Received Path ID 0, Local Path ID 1, version 5
         Extended community: RT:9:9 
   +      Originator: 10.0.0.7, Cluster list: 10.0.0.5             <------- FROM RR xrd05
         PSID-Type:L3, SubTLV Count:1
         SubTLV:
   +        T:1(Sid information), Sid:fc00:0:7777::, Behavior:63, SS-TLV Count:1   <-- SRv6 Locator for source node
           SubSubTLV:
             T:1(Sid structure):
     Path #2: Received by speaker 0
     Not advertised to any peer
     Local
       fc00:0:7777::1 (metric 3) from fc00:0:6666::1 (10.0.0.7)
         Received Label 0xe0040
         Origin incomplete, metric 0, localpref 100, valid, internal, import-candidate, not-in-vrf
         Received Path ID 0, Local Path ID 0, version 0
         Extended community: RT:9:9 
   +      Originator: 10.0.0.7, Cluster list: 10.0.0.6             <------- FROM RR xrd06
         PSID-Type:L3, SubTLV Count:1
         SubTLV:
           T:1(Sid information), Sid:fc00:0:7777::, Behavior:63, SS-TLV Count:1
           SubSubTLV:
             T:1(Sid structure):
   ```

## Configure SRv6-TE steering for L3VPN
**Rome's** L3VPN IPv4 prefixes are associated with two classes of traffic:

* The **"40"** destination (40.0.0.0/24) is bulk transport destination (content replication or data backups) and thus latency and loss tolerant. 
  
* The **"50"** destination (50.0.0.0/24) is for real time traffic (live video, etc.) and thus require the lowest latency path available.

We will use the below diagram for reference:

![L3VPN Topology](/topo_drawings/lab2-l3vpn-policy.png)

### Create SRv6-TE steering policy
For our SRv6-TE purposes we'll leverage the on-demand nexthop (ODN) feature set. Here is a nice example and explanation of ODN: [HERE](https://xrdocs.io/design/blogs/latest-converged-sdn-transport-ig)

In our lab we will configure **rome-xrd07** as the egress PE router with the ODN method. This will trigger **rome-xrd07** to advertise its L3VPN routes with *`color extended communities`*. We'll do this by first defining the *`extcomms`*, then setting up route-policies to match on destination prefixes and set the *`extcomm`* values.

The ingress PE, **london-xrd01**, will then be configured with SRv6 segment-lists and SRv6 ODN steering policies that match routes with the respective color and apply the appropriate SID stack on outbound traffic.

1. Prior to configuring SRv6-TE policy lets get a baseline look at our vpvn4 route as viewed from **london-xrd01**
   Run the following command:
   ```
   show bgp vpnv4 uni vrf carrots 40.0.0.0/24
   ```

   ```diff
   RP/0/RP0/CPU0:xrd01#show bgp vpnv4 uni vrf carrots 40.0.0.0/24
   Thu Jan 23 17:12:01.018 UTC
   BGP routing table entry for 40.0.0.0/24, Route Distinguisher: 10.0.0.1:0
   Versions:
     Process           bRIB/RIB   SendTblVer
     Speaker                 63           63
   Last Modified: Jan 23 17:11:58.418 for 00:00:02
   Paths: (1 available, best #1)
     Not advertised to any peer
     Path #1: Received by speaker 0
     Not advertised to any peer
     Local
       fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
   +     Received Label 0xe0060
         Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, imported
         Received Path ID 0, Local Path ID 1, version 63
   +     Extended community: RT:9:9
         Originator: 10.0.0.7, Cluster list: 10.0.0.5
         PSID-Type:L3, SubTLV Count:1
          SubTLV:
   +       T:1(Sid information), Sid:fc00:0:7777::(Transposed), Behavior:63, SS-TLV Count:1
               SubSubTLV:
             T:1(Sid structure):
         Source AFI: VPNv4 Unicast, Source VRF: default, Source Route Distinguisher: 10.0.0.7:1
   ```
      
2. On **rome-xrd07** configure ext-comms, route-policies, and BGP such that *rome-xrd07* advertises Rome's "40" and "50" prefixes with their respective color extended communities:

   Using the visual code extension, SSH into *rome-xrd07* and paste the following commands:

   ```yaml
   conf t
   extcommunity-set opaque bulk-transfer
     40
   end-set
 
   extcommunity-set opaque low-latency
     50
   end-set

   route-policy set-color
     if destination in (40.0.0.0/24) then
       set extcommunity color bulk-transfer
     endif
     if destination in (50.0.0.0/24) then
       set extcommunity color low-latency
     endif
     pass
   end-policy

   router bgp 65000
   neighbor-group xrd-ipv6-peer
     address-family vpnv4 unicast
     route-policy set-color out
    
     address-family vpnv6 unicast
     route-policy set-color out
   commit
   ```

4. Validate vpnv4 prefixes are received at **london-xrd01** and that they have their color extcomms:
   

   Using the visual code extension, SSH into xrd01 and paste the following commands:


   ```
   show bgp vpnv4 uni vrf carrots 40.0.0.0/24 
   show bgp vpnv4 uni vrf carrots 50.0.0.0/24
   ```
   
   Example:
   ```diff
   RP/0/RP0/CPU0:xrd01#show bgp vpnv4 uni vrf carrots 40.0.0.0/24
    <snip>
     Local
       fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
         Received Label 0xe0060
         Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, imported
         Received Path ID 0, Local Path ID 1, version 67
   +     Extended community: Color:40 RT:9:9
         Originator: 10.0.0.7, Cluster list: 10.0.0.5
         PSID-Type:L3, SubTLV Count:1
          SubTLV:
           T:1(Sid information), Sid:fc00:0:7777::(Transposed), Behavior:63, SS-TLV Count:1
            SubSubTLV:
             T:1(Sid structure):
         Source AFI: VPNv4 Unicast, Source VRF: default, Source Route Distinguisher: 10.0.0.7:1
   ```

2. On **london-xrd01** configure a pair of SRv6-TE segment lists for steering traffic over these specific paths through the network: 
    - Segment list *xrd2347* will execute the explicit path: xrd01 -> 02 -> 03 -> 04 -> 07
    - Segment list *xrd567* will execute the explicit path: xrd01 -> 05 -> 06 -> 07

   **london-xrd01**
   ```yaml
   conf t
   segment-routing
    traffic-eng
     segment-lists
      srv6
       sid-format usid-f3216
      
      segment-list xrd2347
       srv6
        index 10 sid fc00:0:2222::
        index 20 sid fc00:0:3333::
        index 30 sid fc00:0:4444::

      segment-list xrd567
       srv6
        index 10 sid fc00:0:5555::
        index 20 sid fc00:0:6666::
     commit
   ```

3. On **london-xrd01** configure our bulk transport and low latency SRv6 steering policies. Low latency traffic will be forced over the *xrd01-05-06-07* path, and bulk transport traffic will take the longer *xrd01-02-03-04-07* path:
  
   **london-xrd01**
   ```yaml
   conf t
   segment-routing
   traffic-eng
     policy bulk-transfer
     srv6
       locator MyLocator binding-sid dynamic behavior ub6-insert-reduced
     
     color 40 end-point ipv6 fc00:0:7777::1
     candidate-paths
       preference 100
       explicit segment-list xrd2347
      
     policy low-latency
     srv6
       locator MyLocator binding-sid dynamic behavior ub6-insert-reduced
    
     color 50 end-point ipv6 fc00:0:7777::1
     candidate-paths
       preference 100
       explicit segment-list xrd567
     commit
   ```

4. Validate **london-xrd01's** SRv6-TE SID policy is enabled and up:
   ```
    show segment-routing srv6 sid
   ```
   ```
    show segment-routing traffic-eng policy
   ```
   ```
    show bgp vpnv4 uni vrf carrots 40.0.0.0/24 
   ```
   
   Example output, note the additional uDT VRF carrots and SRv6-TE **uB6 Insert.Red** SIDs added to the list:
   ```diff
   RP/0/RP0/CPU0:xrd01#  show segment-routing srv6 sid
   Sat Dec 16 02:45:31.772 UTC
 
   *** Locator: 'MyLocator' *** 

   SID                         Behavior          Context                           Owner               State  RW
   --------------------------  ----------------  --------------------------------  ------------------  -----  --
   fc00:0:1111::               uN (PSP/USD)      'default':4369                    sidmgr              InUse  Y 
   fc00:0:1111:e000::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0:P       isis-100            InUse  Y 
   fc00:0:1111:e001::          uA (PSP/USD)      [Gi0/0/0/1, Link-Local]:0         isis-100            InUse  Y 
   fc00:0:1111:e002::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0:P       isis-100            InUse  Y 
   fc00:0:1111:e003::          uA (PSP/USD)      [Gi0/0/0/2, Link-Local]:0         isis-100            InUse  Y 
   fc00:0:1111:e004::          uDT6              'default'                         bgp-65000           InUse  Y 
   fc00:0:1111:e005::          uDT4              'default'                         bgp-65000           InUse  Y 
   +fc00:0:1111:e006::          uB6 (Insert.Red)  'srte_c_50_ep_fc00:0:7777::1' (50, fc00:0:7777::1)  xtc_srv6            InUse  Y 
   +fc00:0:1111:e007::          uB6 (Insert.Red)  'srte_c_40_ep_fc00:0:7777::1' (40, fc00:0:7777::1)  xtc_srv6            InUse  Y 
   fc00:0:1111:e008::          uDT4              'carrots'                         bgp-65000           InUse  Y 
   fc00:0:1111:e009::          uDT6              'carrots'                         bgp-65000           InUse  Y 
   ```
   
   ```diff
   RP/0/RP0/CPU0:xrd01#show segment-routing traffic-eng policy color 40
   SR-TE policy database
   ---------------------

   Color: 40, End-point: fc00:0:7777::1
     Name: srte_c_40_ep_fc00:0:7777::1
       Status:
   +      Admin: up  Operational: up for 00:09:43 (since Jan 23 17:37:50.369)
       Candidate-paths:
        Preference: 100 (configuration) (active)
         Name: bulk-transfer
         Requested BSID: dynamic
         Constraints:
           Protection Type: protected-preferred
           Maximum SID Depth: 25
   +     Explicit: segment-list xrd2347 (valid)
           Weight: 1, Metric Type: TE
             SID[0]: fc00:0:2222::/48
                     Format: f3216
                     LBL:32 LNL:16 FL:0 AL:80
             SID[1]: fc00:0:3333::/48
                     Format: f3216
                     LBL:32 LNL:16 FL:0 AL:80
             SID[2]: fc00:0:4444::/48
                     Format: f3216
                     LBL:32 LNL:16 FL:0 AL:80
         SRv6 Information:
           Locator: MyLocator
           Binding SID requested: Dynamic
           Binding SID behavior: uB6 (Insert.Red)
     Attributes:
   +    Binding SID: fc00:0:1111:e009::
       Forward Class: Not Configured
       Steering labeled-services disabled: no
       Steering BGP disabled: no
       IPv6 caps enable: yes
       Invalidation drop enabled: no
       Max Install Standby Candidate Paths: 0
       Path Type: SRV6
   ```
   
   ```diff
   RP/0/RP0/CPU0:xrd01#show bgp vpnv4 uni vrf carrots 40.0.0.0/24
    <snip>
     Local
       fc00:0:7777::1 (metric 3) from fc00:0:5555::1 (10.0.0.7)
         Received Label 0xe0040
         Origin incomplete, metric 0, localpref 100, valid, internal, best, group-best, import-candidate, imported
         Received Path ID 0, Local Path ID 1, version 30
   +     Extended community: Color:40 RT:9:9                      
         Originator: 10.0.0.7, Cluster list: 10.0.0.5
   +     SR policy color 40, up, not-registered, bsid fc00:0:1111:e009::   <---- Newly Configured Color Policy 
   
         PSID-Type:L3, SubTLV Count:1
         SubTLV:
           T:1(Sid information), Sid:fc00:0:7777::, Behavior:63, SS-TLV Count:1
           SubSubTLV:
             T:1(Sid structure):
         Source AFI: VPNv4 Unicast, Source VRF: default, Source Route Distinguisher: 10.0.0.7:1
   ```
### Validate SRv6-TE steering of L3VPN traffic

**Validate bulk traffic takes the non-shortest path: london-xrd01 -> 02 -> 03 -> 04 -> rome-xrd07** 

1. Lets now tie the SRv6 TE policy configured to what we expect to see in the Edgeshark output. What you're looking for in the below output is the translation of the previously configured SRv6 TE policy reflected in the actual SRv6 packet header. So the TE bulk policy configured was:

   ```
      segment-list xrd2347
       srv6
        index 10 sid fc00:0:2222::
        index 20 sid fc00:0:3333::
        index 30 sid fc00:0:4444::
   ```
   And we expect to see in the packet header the follow tag order shown below in the capture output:
   ```
   2222:3333:7777
   ```
> [!IMPORTANT]
> Notice that the above that the above SID stack the last hop **zurich-xrd04** (4444). As mentioned in the lecture XR looks at the penultimate hop and does a calculation using the ISIS topology table and determines that **berlin-xrd03's** best forwarding path to **rome-xrd07** (7777) is through **xrd04**. Therefore for efficiency it drops the penultimate hop off the SID stack.

2. Using the Visual Code extension, attach to the **London container's** shell and run a ping to the bulk transport destination IPv4 address on Rome.
    ![London ping](../topo_drawings/lab2-amsterdam-ping.png)

    ```
    ping 40.0.0.1 -i .5
    ```
    
3. Launch an edgeshark capture on container xrd01 interface Gig0/0/0/1 to inspect the traffic.
   
   ![Amsterdam edgeshark](../topo_drawings/lab2-xrd-edgeshark-g0.png) 
   
   Here is a visual representation of our capture :
   
   ![Amsterdam edgeshark](../topo_drawings/lab2-xrd-edgeshark-pcap.png) 
   
   If we focus on the IPv6 header (Outer Header - SRv6 transport layer) we can see the following:


   - Source IPv6: fc00:0:1111::1 
   - Destination IPv6: fc00:0:2222:3333:7777:e006:: which defines the SRv6 segment created earlier for traffic steering accross xrd02, xrd03, xrd04 and xrd07
    
  
**Validate low latency traffic takes the path: london-xrd01 -> 05 -> 06 -> rome-xrd07**

1.  Start a new edgeshark capture  **london-xrd01's** outbound interface (Gi0-0-0-2) to **paris-xrd05**:

    ![Amsterdam edgeshark](../topo_drawings/lab2-xrd-edgeshark-g2.png) 

2.  Let's test and validate that our SRv6 TE policy is applied on **london-xrd01**. From **Amsterdam** we will ping **Rome's** low latency IPv4 destination:
    ```
    ping 50.0.0.1 -i .5
    ```

    ![Amsterdam Capture](../topo_drawings/lab2-xrd-edgeshark-pcap-fast.png) 


    Note the explicit segment-list we configured for our low latency policy:

    ```
    segment-list xrd567
       srv6
         index 10 sid fc00:0:5555::
         index 20 sid fc00:0:6666::
    ```

    Normally we might expect the tcpudmp output to show *5555:6666:7777* in the packet header, however, when the XRd headend router performs its SRv6-TE policy calculation it recognized that **paris-xrd05's** best path to **rome-xrd07** is through **barcelona-xrd06**, so it doesn't need to include the *6666* in the SID stack.


## End of Lab 2
Please proceed to [Lab 3](https://github.com/cisco-asp-web/LTRSPG-2212/blob/main/lab_3/lab_3-guide.md)
