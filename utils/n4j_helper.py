import logging
from typing import List, Mapping
from neo4j import GraphDatabase
import os

logger = logging.getLogger(__name__)

# Define correct URI and AUTH arguments (no AUTH by default)
URI = "bolt://localhost:7687"
AUTH = ("", "")

def Initialize():
    try:
        client = GraphDatabase.driver(URI, auth=AUTH)
        # Check the connection
        client.verify_connectivity()
        return client
    except:
        print("Cannot connect to server at %s" % URI)
        exit(1)
        

INSTANCE = Initialize()

def GetPathID(originPath: str) -> str:
    return '.'.join(str(os.path.abspath(originPath))[1:].split('/'))

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
        parameters_=crafted_params,
        database_="memgraph"
    )
    
    return records[0]["id"]

def FindNodeRegex(regexName: str, pathID: str) -> List[int]:
    records, _, _ = INSTANCE.execute_query(
        """
        MATCH (u:$id:resource)
        WHERE u.name =~ $regex
        RETURN ID(u) as id;
        """,
        id = pathID,
        regex=regexName,
        database_="memgraph"
    )
    return [elem["id"] for elem in records]


def CompressNode(regexName: str, pathID: str):

    node_ids = FindNodeRegex(regexName, pathID)
    # SELECT first as representative, otherwise delete
    representative = node_ids[0]

    # Set representative
    _ = INSTANCE.execute_query(
        """
        MATCH (u:$id:resource)
        WHERE ID(u) = $nodeid
        SET u:compressed
        RETURN *
        """,
        id = pathID,
        nodeid=representative,
        database_="memgraph"
    )
    
    records, _, _ = INSTANCE.execute_query(
        """
            MATCH (u:$id:resource), (v:$id:resource), f=(s:$id)-[]->(u), g=(v)-[]->(d:$id)
            WHERE NOT u:compressed AND NOT v:compressed AND u.name =~ $regex AND v.name =~ $regex
            DETACH DELETE u,v
            
            MATCH (k:$id:resource)
            WHERE ID(k)=$nodeid

            WITH k, collect(s) as cs, collect(d) as cd
            UNWIND cs as ucs
            UNWIND cd as ucd
            MERGE (ucs)-[:REF]->(k)
            MERGE (k) -[:REF]->(ucd)
            return *;
        """,
        id = pathID,
        regex=regexName,
        nodeid=representative,
        database_="memgraph"
    )
    pass

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