import json
from arango import ArangoClient

user = "root"
pw = "jalapeno"
dbname = "jalapeno"

client = ArangoClient(hosts='http://198.18.128.101:30852')
db = client.db(dbname, username=user, password=pw)

# Get the fabric_graph collection
fabric_graph = db.collection('fabric_graph')

# AQL query to update all documents in fabric_graph collection
aql = """
FOR doc IN fabric_graph
    UPDATE doc WITH { load: 0 } IN fabric_graph
    RETURN NEW
"""

# Execute the query
result = db.aql.execute(aql)
count = len(list(result))
print(f"Successfully updated {count} documents in fabric_graph collection")

