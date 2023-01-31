#!/bin/zsh
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"


resourcegroup=$(cat ../../cohesity.json | jq '."resource_group"')
workspacename=$(cat ../../cohesity.json | jq '."workspace_name"')
producer_fun_prefix=$(cat ../../cohesity.json | jq '."workspace_name"')
producer_context=$(cat ../../cohesity.json | jq '."workspace_name"')
consumer_fun_prefix=$(cat ../../cohesity.json | jq '."workspace_name"')
consumer_context=$(cat ../../cohesity.json | jq '."workspace_name"')

./remove.py "$producer_fun_prefix" "$resourcegroup"
./remove.py "$consumer_fun_prefix" "$resourcegroup"
./deploy_config.sh "$workspacename" "$resourcegroup"
./deploy.py "$producer_fun_prefix" "./$producer_context/"
./deploy.py "$consumer_fun_prefix" "./$consumer_context/"
