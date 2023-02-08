#!/bin/zsh
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

. ../../json_parser.sh

./remove.py "$producer_fun_prefix" "$resourcegroup"
./remove.py "$consumer_fun_prefix" "$resourcegroup"
./deploy_config.sh "$workspacename" "$resourcegroup"
# ./deploy.py "$producer_fun_prefix" "./$producer_context/"
# ./deploy.py "$consumer_fun_prefix" "./$consumer_context/"
