#!/bin/zsh
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

if [ -z "$1" ]
then
    workspacename="auto-deploy-workspace"
else
    workspacename="$1"
fi

if [ -z "$2" ]
then
    resourcegroup="ying-test-resource-group"
else
    resourcegroup="$2"
fi

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
    --parameters ApiKey="33e44eac-ce99-46df-7f4e-9ac39446a66e" \
    --parameters ClientId="cf58a81b-bfc5-4942-9f5e-9cdc8d1d119d" \
    --parameters ClientKey="Xzf8Q~SxY28H4UA6fd70bt39DB92xoweNC_RRc_y" \
    --parameters StartDaysAgo="-30" \
    --parameters Workspace="$workspacename"
