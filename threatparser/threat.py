import logging
from enum import Enum
from typing import List
from dfdgraph import DataFlow, DFDNode

logger = logging.getLogger(__name__)
class ActorType(Enum):
    EXTERNAL = "ExternalService"
    CLOUD = "CloudApplication"
    RUSER = "RemoteUser"
    COMPL_MGR = "ComplianceManager"
    VM = "VirtualMachine"
    CONTAINER = "Container"
    HSTORAGE = "HostStorage"
    CSOCKET = "ContainerSocket" # ?
    CVOLUME = "ContainerVolume"


# class ThreatType(Enum):
#     FLOW = "flow"
#     SINGLE = "single" # TODO: implement this in list

"""
----- Specific Mapping -----
External Entities + name="User" = Remote User & Compliance Manager (TODO: find way to discriminate between those 2)
Process = Cloud Application
Process + public = External Service // ? OR External Entities
Data Store = Host Storage
TODO: Virtual Machine, Container

"""

def convert(n: DFDNode) -> ActorType:
    if type(n).__name__ == "ExternalEntity":
        if n.name == "User":
            return ActorType.RUSER
        else:
            return ActorType.EXTERNAL
    if type(n).__name__ == "DataStore":
        return ActorType.HSTORAGE
    if type(n).__name__ == "Process":
        return ActorType.CLOUD
    


class Flow:
    def __init__(self, from_: ActorType, to_:ActorType):
        self.from_ = from_
        self.to_ = to_
    def evaluate(self, df: DataFlow):
        # TODO: Add more logic to mapping between nodes & ActorType
        fn = df.fromNode
        tn = df.toNode

        
        if convert(fn) == self.from_ and convert(tn) == self.to_:
            return True
        return False
    
class FlowThreat:
    def __init__(self, threatName = "", description = "", knowledgeBase: List[Flow] = []):
        self.threatName = threatName
        self.description = description
        self.knowledgeBase = knowledgeBase

    def check(self, df: DataFlow):
        return any(kb.evaluate(df) for kb in self.knowledgeBase)
    
    def read() -> List["FlowThreat"]:
        import csv
        
        result: List["FlowThreat"] = []
        
        logger.info("Opening ./data/threats.csv")
        count = 0
        with open("./data/threats.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                result.append(FlowThreat(
                    row[0],
                    row[1],
                    [Flow(ActorType(i.split(' ')[1]), 
                          ActorType(i.split(' ')[3])) for i in row[2].split('; ')] # TODO: Optimize
                ))
                count += 1
                pass
        logger.info("Loaded " + str(count) + " threats")
                
        return result
    
if __name__ == "__main__":
    x = FlowThreat.read()