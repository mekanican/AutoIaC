from string import ascii_letters
from random import choices
from git import Repo
from glob import glob
import os
import hcl2
import json

# Clone a project to temporary folder
# Only public repository get cloned
def clone_temp(url: str) -> str:
    tempLoc = "/tmp/" + choices(ascii_letters, k = 10)
    while os.path.exists(tempLoc):
        tempLoc = "/tmp/" + choices(ascii_letters, k = 10)
    Repo.clone_from(url, tempLoc).close()
    return tempLoc




def parse_project_JSON(folderPath: str) -> str:
    # Parse root first
    tfList = glob(folderPath + "/*.tf")
    tfvarList = glob(folderPath + "/*.tfvars")
    
    data = hcl2.api.load(open(tfList[-1], "r"))

    print(tfList)
    print(json.dumps(data, indent=2))
    pass


if __name__ == "__main__":
    parse_project_JSON("../KaiMonkey/terraform/aws")