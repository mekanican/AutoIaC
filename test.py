from graph.graph import LoadFromFolder
import os

if __name__ == "__main__":
    os.environ["TOFU"] = "1"
    LoadFromFolder("../cloud_s3/terraform", False)