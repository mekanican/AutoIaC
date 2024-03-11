from typing import List, Mapping
from neo4j import GraphDatabase

# Define correct URI and AUTH arguments (no AUTH by default)
URI = "bolt://localhost:7687"
AUTH = ("", "")

def Initialize():
    client = GraphDatabase.driver(URI, auth=AUTH)
    # Check the connection
    client.verify_connectivity()
    return client

INSTANCE = Initialize()

def CreateNode(labels: List[str], values: Mapping[str, str]) -> int:
    """Create Node in Memgraph

    Args:
        labels (List[str]): _description_
        values (Mapping[str, str]): _description_

    Returns:
        int: _description_
    """
    """
        Labels contain 2 value (any order is ok):
            - encoded target project's path (due to restriction in memgraph for multi-tenant db, so that every node lives in single db)
            - type of resource
        Values contain 3 value:
            - parent id (path of module)
            - resource type
            - resource name
            - (...) additional value to be added later
    """
    crafted_params = {
        "l1" : labels[0],
        "l2" : labels[1],
        "pid": values["parent_id"],
        "rt": values["resource_type"],
        "rn": values["resource_name"],
    }

    records, _, _ = INSTANCE.execute_query(
        "CREATE (u:$l1:$l2 {parent: $pid, type: $rt, name: $rn}) RETURN ID(u) as id;",
        parameters_=crafted_params
    )
    
    return records[0]["id"]

def AddConnection(fromId, targetId):
    """Add connection between 2 node in neo4j database
    """


    records, summary, keys = INSTANCE.execute_query(
        """
            MATCH (c1), (c2)
            WHERE ID(c1) = $id1 AND ID(c2) = $id2
            CREATE (c1)-[r:REF]->(c2)
            RETURN r;
        """,
        id1 = fromId,
        id2 = targetId,
        database_="memgraph"
    )