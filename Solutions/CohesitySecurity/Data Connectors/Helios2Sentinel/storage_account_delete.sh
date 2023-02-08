#!/bin/zsh
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

. ../../json_parser.sh

function get_storage_account_by_prefix()
{
    az storage account list \
        -g "$resourcegroup" \
        | jq --arg v "$1" '.[] | select(.name|test($v)) | .name'
}

function delete_storage_account_by_prefix()
{
    STORAGE_ACCOUNT_TO_DELETED=$(get_storage_account_by_prefix "$1")
    echo "STORAGE_ACCOUNT_TO_DELETED --> $STORAGE_ACCOUNT_TO_DELETED"
    az storage account delete \
        --yes \
        -n "$STORAGE_ACCOUNT_TO_DELETED" \
        -g "$resourcegroup"
}

for ss in \
    "$producer_fun_prefix" \
    "$consumer_fun_prefix"
do
    echo "storage account prefix --> $ss"
    delete_storage_account_by_prefix "$ss"
done
