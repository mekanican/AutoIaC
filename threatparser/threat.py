from enum import Enum
from typing import List
from dfdgraph import DataFlow

class ActorType(Enum):
    EXTERNAL = "ExternalService"
    CLOUD = "CloudApplication"
    RUSER = "RemoteUser"
    COMPL_MGR = "ComplianceManager"
    VM = "VirtualMachine"
    CONTAINER = "Container"
    HSTORAGE = "HostStorage"


# class ThreatType(Enum):
#     FLOW = "flow"
#     SINGLE = "single" # TODO: implement this in list

"""
----- Specific Mapping -----
External Entities + name="User" = Remote User & Compliance Manager (TODO: find way to discriminate between those 2)
Process = Cloud Application
Process + public = External Service
Data Store = Host Storage
TODO: Virtual Machine, Container

"""


class Flow:
    def __init__(self, from_: ActorType, to_:ActorType):
        self.from_ = from_
        self.to_ = to_
    def evaluate(self, df: DataFlow):
        # TODO: Add more logic to mapping between nodes & ActorType
        pass 
    
class FlowThreat:
    def __init__(self, threatName = "", description = "", knowledgeBase: List[any] = []):
        self.threatName = threatName
        self.description = description
        self.knowledgeBase = knowledgeBase
    def parse() -> List["FlowThreat"]:
        import csv
        
        result: List["FlowThreat"] = []
        
        with open("./data/threats.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                result.append(FlowThreat(
                    row[0],
                    row[1],
                    [Flow(i.split(' ')[1], i.split(' ')[3]) for i in row[2].split('; ')] # TODO: Optimize
                ))
                pass
                
        return result
    
if __name__ == "__main__":
    x = FlowThreat.parse()