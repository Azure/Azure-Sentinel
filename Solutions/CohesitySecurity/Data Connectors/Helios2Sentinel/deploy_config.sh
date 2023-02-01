#!/bin/zsh
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

resourcegroup=$(cat ../../cohesity.json | jq '."resource_group"' | sed 's/^"//g;s/"$//g')
workspacename=$(cat ../../cohesity.json | jq '."workspace_name"' | sed 's/^"//g;s/"$//g')
apiKey=$(cat ../../cohesity.json | jq '."apiKey"' | sed 's/^"//g;s/"$//g')
ClientId=$(cat ../../cohesity.json | jq '."ClientId"' | sed 's/^"//g;s/"$//g')
ClientKey=$(cat ../../cohesity.json | jq '."ClientKey"' | sed 's/^"//g;s/"$//g')
StartDaysAgo=$(cat ../../cohesity.json | jq '."StartDaysAgo"' | sed 's/^"//g;s/"$//g')

az monitor log-analytics workspace delete \
    --force \
    --yes \
    --resource-group "$resourcegroup" \
    --workspace-name "$workspacename"

az monitor log-analytics workspace create \
    -g "$resourcegroup" \
    -n "$workspacename"

az deployment group create \
    --name ExampleDeployment \
    --resource-group "$resourcegroup" \
    --template-file ./azuredeploy.json \
    --parameters ApiKey="$apiKey" \
    --parameters ClientId="$ClientId" \
    --parameters ClientKey="$ClientKey" \
    --parameters StartDaysAgo="$StartDaysAgo" \
    --parameters Workspace="$workspacename"
