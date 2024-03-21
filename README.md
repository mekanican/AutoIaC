# AutoIaC
Automated App to convert IaCs scripts to DFD

## Sample architecture:
![](./architecture/main.png)

## Step
0. Run `memgraph` with: `docker compose -f ./memgraph-compose.yaml up`
1. Install Terraform CLI or OpenTofu manually or run `prepare.sh`
- https://developer.hashicorp.com/terraform/install?product_intent=terraform
- https://github.com/opentofu/opentofu
2. Install [Terraform Graph Beautifier](https://github.com/pcasteran/terraform-graph-beautifier) (Make sure the executable is accessible from PATH)

```
go install github.com/pcasteran/terraform-graph-beautifier@latest
```

3. Create new python virtualenv (venv, pipenv, ...)
4. Install dependencies
- `pip install -r requirements.txt`
6. Analyze with this tool
- `./main.py <terraform_project_path> -o <folder_path_to_store_dfd_dot> `
- `-o ..` part is optional, default to current directory output folder
- `--reinit=False` to disable project reinit (for second run)
- `-a`: specify path to annotation (default to `./input/aws_annotation.yaml`)
- `-s`: specify path to semgrep rule for public boundaries identification (default to `./input/semgrep_rule.yaml`)
- `--rule_path`: specify path to rule of relation (default to `./input/aws_rule.yaml`)
- `--graph_mode=True` to export graph instead of sparta


By default, program will seek for terraform executable, if you want to run the program with OpenTofu, use:
```bash
    TOFU=1; ./main.py ... # in bash
    set -x TOFU 1; ./main.py ... # in fish
```
---
## Annotation structure
- Contain 3 main keys: `processes`, `boundaries` and `data_stores`. The configuration must contain all of these keys.
```yaml
processes:
    # ...
boundaries:
    # ...
data_stores:
    # ...
``` 
- Each key contains an array of info about group and its members. Info structure is the same for process, boundary and data store, there are 3 keys to fulfill: `group_name`, `acctp_name` and `members`. This is where you annotate the terraform resource in to group and showed name on DFD 
```yaml
    - group_name: VirtualMachine # Name of the group
      acctp_name: VirtualMachine # Category in ACCTP for Advanced DFD. It is one of the following:
                                 # CloudApplication: Represent applications/services that have ability of computational in infrastructure, except the virtual machine
                                 # ExternalService: Service that is interracting outside of system
                                 # Container: Service that is related to Container (docker, ECS, ...)
      members:
        # ... 
```
- Each group will have an array of members, mapping from terraform "resource type" to its general name. Structure of member will have 4 keys: `name`, `tf_name`, `can_public` and `compress`
```yaml
        - name: AwsAmplify          # General name of resource type
          tf_name: aws_amplify_\w*  # Resource type in terraform, based on https://registry.terraform.io. This can be string or regex
          compress: true            # Optional, default is false. Compressing matched resource (use with regex tf_name) to a single node 
                                    # in DFD. There will be a tradeoff between Component detection & Data flow detection in this option
          can_public: true          # Optional, default is false. Marked this resource type can be public (accessible by user)
```

## Ruleset structure
- Contain 2 main keys: `relations` and `publics`. The configuration must contain all of these keys.
```yaml
relations:
    # ...
publics:
    # ...
```
### Relations
- `relations` will contains 2 key of rules: owning rules (`own`) & special dataflow rule (`direct_flow`, currently not implemented)
```yaml
    own:
        # ...
    direct_flow:
        # ...
```  
- `own` key contain an array of owning rules, showing which component can be in boundary, or which boundary can be in other boundary. Each rule has 4 keys: `id`, `first_node`, `second_node` and `method`:
```yaml
        - id: subnet2vpc                # Unique name to separate between rules
          first_node: VirtualNetwork    # Group name of first "resource" node to detect
          second_node: Subnet           # Group name of second "resource" node to detect
          method: Backward              # Type of connection between 2 resource. It is one of the following:
                                        # Backward: Second node target First node in dependency graph
                                        # Forward: First node target Second node in dependency graph
                                        # IntersectForward: 2 nodes target a common node (unimplemented)
                                        # IntersectBackward: A common node targets 2 nodes (unimplemented)
```
### Public
- `publics` will contains an array of info about component that can be detected the publicity through semgrep. Each info structure has 2 keys: `id` and `variable`
```yaml
  - id: publicsubnet    # Unique name to separate between rules
    variable: $SN_NAME  # Metavariable name that is declared in semgrep rule (must be resource name)
```
