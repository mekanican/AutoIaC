import yaml

def read_config(filePath: str) -> object:
    with open(filePath, "r") as f:
        return yaml.load(f, Loader=yaml.Loader)