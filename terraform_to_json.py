#!/usr/bin/env
from random import choices
import os
from subprocess import run
import logging

logger = logging.getLogger(__name__)

# Json from terraform proj
def GetJSON(folderPath: str) -> str:
    # check if folderPath exist
    if not os.path.exists(folderPath):
        raise Exception("Cannot found specified folder path!")
    
    InitTerraform(folderPath)
    dotPath = GenerateDotFile(folderPath)
    jsonPath = GenerateJSON(dotPath)
    return jsonPath    

def GetRandomTmpPath(suffix: str = ".dot") -> str:
    name = ''.join(choices("abcdefghABCDEFGH12345678", k=8))
    return "/tmp/" + name + suffix

def InitTerraform(folderPath):
    # Cleanup
    command = [
            "rm",
            "-rf",
            folderPath + ".terraform",
            folderPath + ".terraform.lock.hcl"
    ]

    logger.info("Running %s" % ' '.join(command)) 
    run(command)
    # Init
    command = [
            "tofu",
            "-chdir=%s"%folderPath,
            "init"
    ]

    logger.info("Running %s" % ' '.join(command)) 
    run(command, check=True)

# tofu graph -chdir ../aws_vpc_msk/
def GenerateDotFile(folderPath: str) -> str:
    command = [
            "tofu",
            "-chdir=%s"%folderPath,
            "graph"
    ]

    logger.info("Running %s" % ' '.join(command)) 
    result = run(command, capture_output=True, check=True)
    
    path = GetRandomTmpPath()
    logger.info("Writting to %s" % path)

    with open(path, "wb") as f:
        f.write(result.stdout)

    return path

def GenerateJSON(dotPath: str) -> str:
    command = [
            "terraform-graph-beautifier",
            "-input",
            dotPath,
            "--output-type=cyto-json"
    ]

    logger.info("Running %s" % ' '.join(command)) 
    result = run(command, capture_output=True, check=True)
    
    path = GetRandomTmpPath(".json")
    logger.info("Writting to %s" % path)

    with open(path, "wb") as f:
        f.write(result.stdout)

    return path
