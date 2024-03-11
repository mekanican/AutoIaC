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

def AddConnection(fromLabels: List[str], fromValues: Mapping[str, str], toLabels: List[str], toValues: Mapping[str, str]):
    """Add connection between 2 node in neo4j database

    Args:
        fromLabels (List[str]): list of labels for "from" node
        fromValues (Mapping[str, str]): object for storing data of "from" node
        toLabels (List[str]): list of labels for "to" node
        toValues (Mapping[str, str]): object for storing data of "to" node
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
        "fl1" : fromLabels[0],
        "fl2" : fromLabels[1],
        "fpid": fromValues["parent_id"],
        "frt": fromValues["resource_type"],
        "frn": fromValues["resource_name"],

        "tl1" : toLabels[0],
        "tl2" : toLabels[1],
        "tpid": toValues["parent_id"],
        "trt": toValues["resource_type"],
        "trn": toValues["resource_name"],
    }

    records, summary, keys = INSTANCE.execute_query(
        "CREATE (u:$fl1:$fl2 {parent: $fpid, type: $frt, name: $frn}) -[:REF]-> (v:$tl1:$tl2 {parent: $tpid, type: $trt, name: $trn}))",
        parameters_=crafted_params,
        database_="memgraph"
    )
    
    pass