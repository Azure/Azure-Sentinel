#!/bin/zsh
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

./remove.py "cohesitypro" "ying-test-resource-group"
./remove.py "cohesitycon" "ying-test-resource-group"
./deploy_config.sh
./deploy.py "cohesitypro" "./IncidentProducer/"
./deploy.py "cohesitycon" "./IncidentConsumer/"
