#!/bin/zsh
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

. ../../json_parser.sh

az monitor log-analytics workspace delete \
    --force \
    --yes \
    --resource-group "$resourcegroup" \
    --workspace-name "$workspacename"

az monitor log-analytics workspace create \
    -g "$resourcegroup" \
    -n "$workspacename"

./storage_account_delete.sh

az deployment group create \
    --name ExampleDeployment \
    --resource-group "$resourcegroup" \
    --template-file ./azuredeploy.json \
    --parameters ApiKey="$apiKey" \
    --parameters ClientId="$ClientId" \
    --parameters ClientKey="$ClientKey" \
    --parameters StartDaysAgo="$StartDaysAgo" \
    --parameters Workspace="$workspacename"
