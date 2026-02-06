# Lab 2 - Packet Walk: Validate SRv6-TE steering of L3VPN traffic

In the previous section, we validated the SRv6 control plane, confirming that color-based SR policies, Binding SIDs, and segment lists were correctly programmed between the London and Rome sites. We now move to data-plane validation, focusing on how traffic originating from the London container is actually forwarded across the network toward the Rome container. Using SRv6 color-based policies, packets are steered along explicitly engineered paths, independent of default IGP routing. Two traffic intents are validated: a bulk-transfer path and a low-latency path, each traversing a different set of intermediate nodes. By observing packet forwarding and captures along the path, we validate how control-plane intent is enforced in the data plane through SRv6 Binding SIDs and segment lists.

**Validate bulk traffic takes the non-shortest path: london-xrd01 -> 02 -> 03 -> 04 -> rome-xrd07** 

In SRv6 Traffic Engineering, uSIDs allow a source node (ingress PE, London-XRD01 in this case) to explicitly program a packet’s path through a domain by enforcing a sequence of intermediate waypoints or links.

The following diagram illustrates the expected traffic path and highlights the different capture points that will be demonstrated.

![Lab2-Wireshark](../topo_drawings/lab2-topology-wireshark.png)

1. Using the Visual Code extension, ssh to the **London container's** shell and run a ping to the bulk transport destination IPv4 address on Rome. We will capture and analyze this traffic at multiple points across the network.

   ```
    ping 40.0.0.1 -i .5
   ```

![London ping](../topo_drawings/lab2-amsterdam-ping.png)

  Launch an edgeshark capture on the **london-xrd01** container interface Gig0/0/0/0 to inspect the traffic.

![London gi0/0/0](../topo_drawings/lab2-xrd-edgeshark-g0.png)

  Observing the ICMP traffic exchanged between the London and Rome containers, the echo request is a standard IPv4 packet sourced from 10.101.1.2 and destined for 40.0.0.1, with a measured round-trip time of approximately 120 ms. This latency matches the delay values that were intentionally introduced on the links in Lab 1, confirming that traffic is traversing the expected network path.

![London gi0/0/0 capture](../topo_drawings/lab2-xrd01-wireshark-g0.png)


2. Lets now tie the SRv6 TE policy configured to what we expect to see in the Edgeshark output. What you're looking for in the below output is the translation of the previously configured SRv6 TE policy reflected in the actual SRv6 packet header. So the TE bulk policy configured was:

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
> Notice that the above SID stack the last hop **zurich-xrd04** (4444). As mentioned in the lecture XR looks at the penultimate hop and does a calculation using the ISIS topology table and determines that **berlin-xrd03's** best forwarding path to **rome-xrd07** (7777) is through **xrd04**. Therefore for efficiency it drops the penultimate hop off the SID stack.

    
3. Launch an edgeshark capture on container **london-xrd01** interface Gig0/0/0/1 to inspect the traffic.
   
   ![London edgeshark](../topo_drawings/lab2-xrd-edgeshark-g1.png) 
   
   Here is a visual representation of our capture :
   
   ![London edgeshark](../topo_drawings/lab2-xrd-edgeshark-pcap.png) 
   
   If we focus on the IPv6 header (Outer Header - SRv6 transport layer) we can see the following:


   - Source IPv6: fc00:0:1111::1 
   - Destination IPv6: fc00:0:2222:3333:7777:e006:: which defines the SRv6 segment created earlier for traffic steering accross xrd02, xrd03, xrd04 and xrd07
    
In SRv6 Traffic Engineering, uSIDs allow a source node (ingress PE) to explicitly program a packet’s path through a domain by enforcing a sequence of intermediate waypoints or links. Like all Segment Routing, uSID-based TE is stateless; the entire path and service instructions are encoded in the packet header, meaning transit routers do not need to maintain per-flow state.

SRH-style SRv6 requires a 128-bit SID for every hop, which can lead to large packet headers.
uSIDs solve this by packing six hops into a single address, allowing complex TE paths to be executed without a Segment Routing Header (SRH) in most use cases.

On-Demand Next-Hop (ODN) allows the headend to instantiate an SR Policy dynamically only when it receives a service route with a specific color. This eliminates the need to pre-configure "full mesh" tunnels, significantly improving scalability.


4. Launch an edgeshark capture on container **berlin-xrd03** interface Gig0/0/0/0 to inspect the traffic.

  ![Berlin Wireshark Capture](../topo_drawings/lab2-xrd03-wireshark-g0.png)

Like in the previous steps, we need to focus on the IPv6 header (Outer Header - SRv6 transport layer):

   - Source IPv6: fc00:0:1111::1 
   - Destination IPv6: fc00:0:3333:7777:e007:: which defines a modified version of the SRv6 segment created earlier for traffic steering accross xrd02, xrd03, xrd04 and xrd07

Unlike MPLS, which pops labels from a stack, SRv6 microSIDs operate by directly modifying the IPv6 destination address to expose the next forwarding instruction. At each hop, the active uSID is consumed by shifting the remaining uSID fields within the destination address, effectively removing the current instruction and advancing the next one. In this step, the uSID 2222 is consumed at XRD02, resulting in a destination address of fc00:0:3333:7777:e007:: downstream, confirming correct hop-by-hop execution of the SRv6 data plane.


5. Launch an edgeshark capture on container **zurich-xrd04** interface Gig0/0/0/0 to inspect the traffic.

  ![Zurich ingress Wireshark Capture](../topo_drawings/lab2-xrd04-wireshark-g0.png)

Here, the zurich xrd router (XRD04 – 4444) receives a packet whose IPv6 destination address contains the microSID of the final destination (7777) rather than its own, and therefore forwards the packet as standard IPv6 traffic toward the endpoint.

- No SRv6 Processing: The router does not perform any "Shift" operations because the Destination Address does not match any of its locally configured SRv6 SIDs.
- Longest Prefix Match (LPM): The router performs a standard Longest Prefix Match lookup on the Destination Address.
- Forwarding: It finds the route to the final destination (the egress PE or next endpoint) and forwards the packet out the appropriate interface


6. Launch an edgeshark capture on container **rome-xrd07** interface Gig0/0/0/1 to inspect the traffic sent by **Zurich-xrd04**.

  ![Rome ingress Wireshark Capture](../topo_drawings/lab2-xrd07-wireshark-g1.png)

When Rome receives the packet with an IPv6 destination address of fc00:0:7777:e007::, the active microSID (7777) matches Rome’s own uSID, indicating that the packet has reached its final SRv6 endpoint. At this stage, all transit microSIDs have already been consumed, and no further traffic steering is required. Rome therefore executes the endpoint service behavior associated with e007 (for example, uDT4/uDT6: More information [here](https://www.ciscolive.com/c/dam/r/ciscolive/emea/docs/2025/pdf/BRKSPG-2203.pdf) and [here](https://datatracker.ietf.org/doc/html/rfc8986#name-enddt6-decapsulation-and-sp)), decapsulates the packet as needed, and forwards the inner payload according to the local routing or VRF configuration.



7. Launch an edgeshark capture on container **rome-xrd07** interface Gig0/0/0/0 to inspect the traffic.

  ![Rome Wireshark Capture](../topo_drawings/lab2-xrd07-wireshark-g1.png)

At the Rome router, the SRv6 transport header has been fully processed and removed, and the packet is delivered to the endpoint service. As shown in this capture, only a standard IPv4 ICMP packet remains, sourced from 10.101.1.2 and destined for 40.0.0.1, confirming that the outer SRv6 header been decapsulated. This behavior corresponds to the execution of the SRv6 uDT4 endpoint function, which forwards the packet into the correct routing context. The packet is then forwarded within the Carrots VRF, completing the end-to-end SRv6 packet walk from London to Rome.

<br><br>

**Validate low latency traffic takes the path: london-xrd01 -> 05 -> 06 -> rome-xrd07**

> [!NOTE]
> To keep the lab concise, we will not repeat packet captures on every interface for this section. However, students are encouraged to capture traffic on **any interfaces** if they wish to further explore and validate the SRv6 packet walk across the network.

1.  Start a new edgeshark capture  **london-xrd01's** outbound interface (Gi0-0-0-2) to **paris-xrd05**:

2.  Let's test and validate that our SRv6 TE policy is applied on **london-xrd01**. From **app-container-london** we will ping **Rome's** low latency IPv4 destination:
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

    Under normal circumstances, we might expect the packet header to include the microSID sequence *5555:6666:7777*, explicitly steering traffic through **paris-xrd05**, **barcelona-xrd06**, and finally **rome-xrd07**. However, when the XRd headend router computes the SRv6 Traffic Engineering policy, it determines that the best path from paris-xrd05 to **rome-xrd07** naturally traverses **barcelona-xrd06** based on the IGP topology. As a result, the headend optimizes the uSID list by omitting 6666, since no additional steering decision is required at that hop. This optimization reduces SID overhead while still enforcing the intended SRv6-TE path, resulting in an outer IPv6 destination address of *fc00:0:5555:7777:e006::*.

## End of Lab 2 - Packet Walk
Please proceed to [Lab 3](https://github.com/cisco-asp-web/LTRSPG-2212/blob/main/lab_3/lab_3-guide.md)
