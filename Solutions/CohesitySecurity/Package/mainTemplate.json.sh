#!/bin/zsh
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

. ../json_parser.sh

az deployment group create \
    --name ExampleDeployment \
    --resource-group "$resourcegroup" \
    --template-file ./mainTemplate.json \
    --parameters EmailID=cohesity-siem@outlook.com \
    --parameters connector1-name=$(uuidgen) \
    --parameters location=eastasia
