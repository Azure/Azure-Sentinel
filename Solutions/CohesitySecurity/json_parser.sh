#!/bin/zsh
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

client_id=$(cat ./cohesity.json | jq '."client_id"' | sed 's/^"//g;s/"$//g')
client_key=$(cat ./cohesity.json | jq '."client_key"' | sed 's/^"//g;s/"$//g')
start_days_ago=$(cat ./cohesity.json | jq '."start_days_ago"' | sed 's/^"//g;s/"$//g')
api_key=$(cat ./cohesity.json | jq '."api_key"' | sed 's/^"//g;s/"$//g')
consumer_context=$(cat ./cohesity.json | jq '."consumer_context"' | sed 's/^"//g;s/"$//g')
consumer_fun_prefix=$(cat ./cohesity.json | jq '."consumer_fun_prefix"' | sed 's/^"//g;s/"$//g')
producer_context=$(cat ./cohesity.json | jq '."producer_context"' | sed 's/^"//g;s/"$//g')
producer_fun_prefix=$(cat ./cohesity.json | jq '."producer_fun_prefix"' | sed 's/^"//g;s/"$//g')
resource_group=$(cat ./cohesity.json | jq '."resource_group"' | sed 's/^"//g;s/"$//g')
# workspace_name="automate-test-$(uuidgen)"
workspace_name=$(cat ./cohesity.json | jq '."workspace_name"' | sed 's/^"//g;s/"$//g')
user_email=$(cat ./cohesity.json | jq '."user_email"' | sed 's/^"//g;s/"$//g')
workspace_id=$(cat ./cohesity.json | jq '."workspace_id"' | sed 's/^"//g;s/"$//g')
cd -
