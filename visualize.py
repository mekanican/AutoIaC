import dash_interactive_graphviz
import dash
from dash.dependencies import Input, Output
from dash import html


app = dash.Dash(__name__)
app.renderer = '''
var renderer = new DashRenderer({
    request_post: (payload, response) => {
        f()
    }
})
'''

initial_dot_source = """
digraph  {
node[style="filled"]
a ->b->d
a->c->d
}
"""

app.layout = html.Div(
    [
        html.Div(
            dash_interactive_graphviz.DashInteractiveGraphviz(id="gv", engine="dot", dot_source=initial_dot_source),
            style=dict(flexGrow=0.75, position="relative"),
        ),
        html.Div(
            [
                html.H3("Selected resource"),
                html.Div(id="selected"),
                html.H3("Terraform source"),
                html.Div(
                    html.Pre(
                        html.Code(
                            """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region  = "us-west-2"
}

resource "aws_instance" "app_server" {
  ami           = "ami-830c94e3"
  instance_type = "t2.micro"

  tags = {
    Name = "ExampleAppServerInstance"
  }
}
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region  = "us-west-2"
}

resource "aws_instance" "app_server" {
  ami           = "ami-830c94e3"
  instance_type = "t2.micro"

  tags = {
    Name = "ExampleAppServerInstance"
  }
}
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region  = "us-west-2"
}

resource "aws_instance" "app_server" {
  ami           = "ami-830c94e3"
  instance_type = "t2.micro"

  tags = {
    Name = "ExampleAppServerInstance"
  }
}""",
                            id="input",
                            # className="language-hcl",
                            # value=initial_dot_source,
                            # value="resource {}",
                            # readOnly=True,
                            
                        ), className="language-hcl line-numbers"
                    ), style=dict(flexGrow=1, position="relative", overflowY="scroll"),
                )
            ],
            style=dict(display="flex", flexDirection="column", flexGrow=0.25, width="25%"),
        ),
    ],
    style=dict(position="absolute", height="98%", width="99%", display="flex"),
)


# @app.callback(
#     Output("gv", "dot_source"),
#     [Input("input", "value")],
# )
# def display_output(value):
#     return value


@app.callback(Output("selected", "children"), [Input("gv", "selected")])
def show_selected(value):
    return html.Div(value)


if __name__ == "__main__":
    app.run_server(debug=True)