# AutoIaC
Automated App to convert IaCs scripts to DFD

## Step
1. Install Terraform CLI or OpenTofu
- https://developer.hashicorp.com/terraform/install?product_intent=terraform
- https://github.com/opentofu/opentofu
2. Install [Terraform Graph Beautifier](https://github.com/pcasteran/terraform-graph-beautifier)

```
go install github.com/pcasteran/terraform-graph-beautifier@latest
```

3. Create new python virtualenv (venv, pipenv, ...)
4. Install dependencies
- `pip install -r requirements.txt`
- `pip install -r pytm/requirements.txt`
5. Ensure target terraform project is not initialized. If yes, copy project to others directory and remove `.terraform`, `.terraform.lock.hcl`
6. Init project (replace `tofu` with `terraform` if you use terraform cli)
- `tofu -chdir=<path_to_folder> init`
7. Generate graph dotfile
- `tofu -chdir=<path_to_folder> graph > <dot_output_path>`
8. Generate json data from generated dotfile
- `cat <dot_path> | terraform-graph-beautifier --output-type=cyto-json > <json_output_path>`
9. Analyze with this tool
- `./main.py <json_path> -o <folder_path_to_store_dfd_dot> `
- `-o ..` part is optional, default to current directory output folder
