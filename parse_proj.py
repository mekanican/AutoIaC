from string import ascii_letters
from random import choices
from git import Repo
from glob import glob
import os
import hcl2
import json
import logging

logger = logging.getLogger(__name__)

# Clone a project to temporary folder
# Only public repository get cloned
def clone_temp(url: str) -> str:
    tempLoc = "/tmp/" + choices(ascii_letters, k = 10)
    while os.path.exists(tempLoc):
        tempLoc = "/tmp/" + choices(ascii_letters, k = 10)
    Repo.clone_from(url, tempLoc).close()
    return tempLoc




def parse_project_JSON(folderPath: str, allBlock: dict = {}) -> str:
    # Parse root first
    tfList = glob(folderPath + "/*.tf")
    tfvarList = glob(folderPath + "/*.tfvars")
    logger.info(f"Parsing {folderPath}:")
    logger.info(", ".join(tfList))

    for tf in tfList:
        data = hcl2.api.load(open(tf, "r"))
        for k,v in data.items():
            if k not in allBlock:
                allBlock[k] = v
            else:
                allBlock[k] += v # TODO: Find ways to separate module
    
    """
    "module": [
        {
            "network": {
                "source": "./modules/network",
                "environment": "${var.environment}",
                "default_tags": "${var.default_tags}"
            }
        },
    """

    modLocs = []

    for mod in allBlock["module"]:
        k, v = next(iter(mod.items())) 
        # print("[***]",k, v)
        logger.info("Found module " + k + " at " + v["source"])
        # Move module to analyzed to ignore further analyze
        if "analyzed_module" not in allBlock:
            allBlock["analyzed_module"] = {k : v}
        else:
            allBlock["analyzed_module"][k] = v
        modLocs.append(v["source"])
    allBlock["module"] = []
    for v in modLocs:
        parse_project_JSON(folderPath + "/" + v, allBlock)
    
    # print(json.dumps(allBlock, indent=2))



if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    allBlock = {}
    parse_project_JSON("../KaiMonkey/terraform/aws", allBlock)
    print(json.dumps(allBlock, indent=2))