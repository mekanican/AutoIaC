# AutoIaC
Automated App to convert IaCs scripts to DFD

## Sample architecture:
![](./architecture/main.png)

## Step
1. Install Terraform CLI or OpenTofu manually or run `prepare.sh`
- https://developer.hashicorp.com/terraform/install?product_intent=terraform
- https://github.com/opentofu/opentofu
2. Install [Terraform Graph Beautifier](https://github.com/pcasteran/terraform-graph-beautifier)

```
go install github.com/pcasteran/terraform-graph-beautifier@latest
```

3. Create new python virtualenv (venv, pipenv, ...)
4. Install dependencies
- `pip install -r requirements.txt`
6. Analyze with this tool
- `./main.py <terraform_project_path> -o <folder_path_to_store_dfd_dot> `
- `-o ..` part is optional, default to current directory output folder
