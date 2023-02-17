#!/bin/zsh
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

. ../../json_parser.sh

./remove.py
./deploy_config.sh
# ./deploy.py "$producer_fun_prefix" "./$producer_context/"
# ./deploy.py "$consumer_fun_prefix" "./$consumer_context/"
