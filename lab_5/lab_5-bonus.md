## Bonus: Project Jalapeno and Host-Based SRv6

Please consider this Bonus section and the tasks in it to be optional, but hopefully interesting/entertaining.

### Why host-based SRv6? 

* **Flexibility and Control**: We get tremendous control of the SRv6 SIDs and our encapsulation depth isn't subject to ASIC limitations

* **Performance and Massive Scale**: With host-based SRv6 traffic reaches the transport network already encapsulated, thus the ingress PE or SRv6-TE headend doesn't need all the resource intense policy configuration; they just statelessly forward traffic per the SRv6 encapsulation or Network Program
  
* **SRv6 as Common E2E Architecture**: We could extend SRv6 across WAN, Metro, and DC domains, and even into the Cloud! Or to IoT devices or other endpoints connected to the physical network...
 
We feel this ability to perform SRv6 operations at the host or other endpoint is a game changer which opens up enormous potential for innovation!

## Project Jalapeno

A database driven, topology modeling platform designed to enable development of SDN control applications.  The SRv6-PyTorch Plugin is an of an SDN control application developed on top of the Jalapeno platform. In future versions of this lab we expect to add more SDN control use cases.

More info on Jalapeno:

https://github.com/cisco-open/jalapeno


The Jalapeno package is preinstalled and running on the **Jalapeno** VM (198.18.128.101).

1. Optional: SSH to the Jalapeno VM and display the running k8s pods. Those who are new to Kubernetes can reference this cheat sheet [HERE](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)  

    ```
    ssh cisco@198.18.128.101
    ```
    
    Display k8s pods
    ```
    kubectl get pods -A
    ```
    Note that the Jalapeno VM is also using Cilium as its CNI, and that all of the Jalapeno pods/microservices are running in the **jalapeno** namespace.  Also, the Jalapeno K8s cluster is completely independent of the K8s cluster on the Berlin VM. In our simulation the Berlin VM is a consumer of services on our SRv6 network, which may include services that are accessed by interacting with Jalapeno.


### Arango Graph Database
At the heart of Jalapeno is the Arango Graph Database, which is used to model network topology and provide a graph-based data store for the network data collected via BMP or other sources. 

1. Optional: Open the Arango web UI at:

    ```
    http://198.18.128.101:30852/
    ```
    
    Login and select the "jalapeno" DB from the dropdown:
    ```
    user: root
    password: jalapeno
    DB: jalapeno
    ```
    Once logged in the UI will show you its *collections* view. If you like, take a moment to browse around the collections


2. Optional or for reference: connect to the DB and try some of the queries in the [lab_5-arango-queries.md doc](https://github.com/cisco-asp-web/LTRSPG-2212/tree/main/lab_5/lab_5-arango-queries.md)

> [!NOTE]
> This next step affects later tasks in the bonus lab, so for best results it should be completed.

3. Run the *add-meta-data.py* script to upload some synthetic network performance data to the ipv4 and ipv6 graphs that represent the XRd topology from labs 1-3:

   From a terminal session on *topology-host* ssh to the Jalapeno VM (pw = cisco123):
   ```
   ssh -oHostKeyAlgorithms=+ssh-rsa cisco@198.18.128.101
   ```

   Then cd into the lab_5/jalapeno directory and do a *git pull*
   ```
   cd ~/LTRSPG-2212/lab_5/jalapeno/xrd-network/
   git pull
   ```

   Then run the *add-meta-data.py* script
   ```
   python3 add_meta_data.py 
   ```

   Expected output:
   ```
   cisco@jalapeno:~/LTRSPG-2212/lab_5/jalapeno/xrd-network$ python3 add_meta_data.py 
   adding hosts, addresses, country codes, and synthetic latency data to the graph
   adding location, country codes, latency, and link utilization data
   meta data added
   Successfully inserted/updated 3 hosts records
   Successfully inserted/updated 4 IPv4 edge records
   Successfully inserted/updated 6 IPv6 edge records
   ```

### Jalapeno REST API

The Jalapeno REST API is used to run queries against the ArangoDB and retrieve graph topology data or execute shortest path calculations. 

1. Test the Jalapeno REST API:
   From the ssh session on the *jalapeno VM* or the *topology-host VM* give the Jalapeno REST API a try. We installed the *`jq`* tool on the *jalapeno VM* to help with improved JSON parsing:
   ```
   curl http://198.18.128.101:30800/api/v1/collections | jq | more
   ```

   The API has auto-generated documentation at: [http://198.18.128.101:30800/docs/](http://198.18.128.101:30800/docs/) - right-click and open link in new tab

   The Jalapeno API github repo has a collection of example curl commands as well:

   [Jalapeno API Github](https://github.com/jalapeno/jalapeno-api/blob/main/notes/curl-commands.md)


### Jalapeno Web UI

The Jalapeno UI is a demo or proof-of-concept meant to illustrate the potential use cases for extending SRv6 services beyond traditional network elements and into the server, host, VM, k8s, or other workloads. Once Jalapeno has programmatically collected data from the network and built its topology graphs, the network operator has complete flexibility to add data or augment the graph. In fact, our SONiC *`fabric_graph`* data was simply uploaded from a set of json files. 

Once the topology graphs are in place its not too difficult to conceive of building network services based on calls to the Jalapeno API and leveraging the SRv6 uSID stacks that are returned.

The Jalapeno Web UI can be accessed at: [http://198.18.128.101:30700](http://198.18.128.101:30700). 

On the left hand sidebar you will see that UI functionality is split into two sections:

- **Data Collections**: explore raw object and graph data collected from the network.
- **Topology Viewer**: explore the network topology graphs and perform path calculations.

In *Topology Viewer* mode you get a dropdown of all the known *graphs* in the DB. When you select a graph it'll render in the visual pane. From there you can explore different visual representations of the topology with the *layouts* dropdown. You can also perform path calculation operations by clicking on elements in the topology and then selecting a constraint from from the *path constraint* dropdown.

1. Run a path calculation in the UI:

 - Click *Topology Viewer*
 - Select either *ipv4 graph* or *ipv6 graph* from the dropdown
 - In the visual pane click on two of the green nodes (Amsterdam & Rome or Berlin and Rome are a good choice)
 - Once the endpoints are highlighted select a constraint from the *path constraint* dropdown

As you complete the workflow the UI calls the API and feeds it the source/destination pair and constraint. The backend performs a shortest-path calculation based on the selected constraint (leveraging the synthetic meta data we added earlier) and returns a path highlighted in the UI and SID info in a popup.

2. Feel free to try different endpoint combinations and path constraint selections. The *add_meta_data.py* script we added earlier has populated the graphDB with latency, link utilization, at path country code data such that the different constraint selections should produce different path results and SRv6 uSID combinations.