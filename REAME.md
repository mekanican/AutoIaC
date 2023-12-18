# Step to run script
1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `python3 src/handler.py -u <url>`
    - Ouput to `output/work/final`

# Example step to build graph
1. `cd output/work/final/modules/aws-data`
2. `terraform init`
3. `terraform graph | dot -Tpng > graph.png`