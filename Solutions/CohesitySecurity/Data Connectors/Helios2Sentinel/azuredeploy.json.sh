#!/bin/zsh
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

resourcegroup="ying-test-resource-group"
workspacename="auto-deploy-workspace"
producer_fun_prefix="cohesitypro"
producer_context="IncidentProducer"
consumer_fun_prefix="cohesitypro"
consumer_context="IncidentConsumer"

./remove.py "$producer_fun_prefix" "$resourcegroup"
./remove.py "$consumer_fun_prefix" "$resourcegroup"
./deploy_config.sh "$workspacename" "$resourcegroup"
./deploy.py "$producer_fun_prefix" "./$producer_context/"
./deploy.py "$consumer_fun_prefix" "./$consumer_context/"
