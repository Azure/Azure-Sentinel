#!/bin/zsh
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

. ../../json_parser.sh

az monitor log-analytics workspace create \
    -g "$resource_group" \
    -n "$workspace_name"

./storage_account_delete.sh

az deployment group create \
    --name ExampleDeployment \
    --resource-group "$resource_group" \
    --template-file ./azuredeploy.json \
    --parameters ApiKey="$api_key" \
    --parameters ClientId="$client_id" \
    --parameters ClientKey="$client_key" \
    --parameters StartDaysAgo="$start_days_ago" \
    --parameters Workspace="$workspace_name"
