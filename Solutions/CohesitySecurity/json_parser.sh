#!/bin/zsh
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

ClientId=$(cat ./cohesity.json | jq '."ClientId"' | sed 's/^"//g;s/"$//g')
ClientKey=$(cat ./cohesity.json | jq '."ClientKey"' | sed 's/^"//g;s/"$//g')
StartDaysAgo=$(cat ./cohesity.json | jq '."StartDaysAgo"' | sed 's/^"//g;s/"$//g')
apiKey=$(cat ./cohesity.json | jq '."apiKey"' | sed 's/^"//g;s/"$//g')
consumer_context=$(cat ./cohesity.json | jq '."consumer_context"' | sed 's/^"//g;s/"$//g')
consumer_fun_prefix=$(cat ./cohesity.json | jq '."consumer_fun_prefix"' | sed 's/^"//g;s/"$//g')
producer_context=$(cat ./cohesity.json | jq '."producer_context"' | sed 's/^"//g;s/"$//g')
producer_fun_prefix=$(cat ./cohesity.json | jq '."producer_fun_prefix"' | sed 's/^"//g;s/"$//g')
resourcegroup=$(cat ./cohesity.json | jq '."resource_group"' | sed 's/^"//g;s/"$//g')
workspacename=$(cat ./cohesity.json | jq '."workspace_name"' | sed 's/^"//g;s/"$//g')
cd -
