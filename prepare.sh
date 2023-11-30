#!/usr/bin/bash
# Install tofu to /usr/local/bin (single portable file)
if ! command -v tofu &> /dev/null
then
    echo "Tofu not found, installing..."
    ./tofu_install.sh
fi

# Install terraform-graph-beautifier (require go installed)
if ! command -v go &> /dev/null
then
    echo "Install golang before running this script!"
    exit 1
fi

go install github.com/pcasteran/terraform-graph-beautifier@latest
ln -s ~/go/bin/terraform-graph-beautifier /usr/local/bin/terraform-graph-beautifier
