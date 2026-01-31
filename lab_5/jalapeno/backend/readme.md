## Quick guide to Jalapeno sonic-network

**add-data.py** - uploads the SONiC fabric data including nodes, hosts, srv6 data, and connections into the graphDB

*Usage*: 
```
python3 add-data.py -d all
```

**fabric-graph.json**
The json file containing sonic and ubuntu host nodes, and how they connect to one another in the graph. The *add-data.py* script uses this data to create the graphDB *edge* collection that the API calls when making fabric load balancing path calculations.

**fabric-node.json** 
The SONiC nodes and their relevant (SRv6) attributes to be populated in the graphDB by *add-data.py*

**hosts.json**
The Ubuntu "host" containers' data to be uploaded into the graphDB by *add-data.py*

**latency-util.json**
A set of static latency and utilization metrics that *add-data.py* uploads to the graphDB edge collection. (for future use)

**clear-load.py**
The fabric load balancing API is running shortest-path queries against the graphDB using *`load`* as the metric. Every time a new path is requested the API increments the *load* value on each link in the selected path, thus making it a more costly path for future API calls (good enough for demo purposes!). Use the *clear-load.py* script to zero-out the *load* values across the fabric graph.

*Usage*:
```
python3 clear-load.py
```
