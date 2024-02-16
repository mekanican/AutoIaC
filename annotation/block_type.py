from enum import Enum

class BlockType(Enum):
    RESOURCE    = "resource"
    OUTPUT      = "output"
    VARIABLE    = "var"
    MODULE      = "module"
    PROVIDER    = "provider" 
    LOCAL       = "local"
    DATA        = "data"