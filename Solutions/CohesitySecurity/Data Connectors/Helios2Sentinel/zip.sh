#!/bin/zsh
# This script is used to publish the 2 function apps into 2 zip files, for later azure deployment.
# no input needed, and it could be run from any where.

set -o nounset
set -o errexit
set -o pipefail
set +o noclobber

SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

dotnet clean
dotnet publish -c Release
PUBLISH_DIR="./bin/Release/net6.0/publish/"

find "$SCRIPTPATH"/ -type f -iname \*.csproj | while read ss; \
do \
    SCRIPT=$(realpath "$ss")
    CSPROJDIR=$(dirname "$SCRIPT")
    cd "$CSPROJDIR"

    filename=$(basename -- "$ss")
    extension="${filename##*.}"
    filename="${filename%.*}"
    cd "$PUBLISH_DIR"
    zip -r ./"$filename".zip ./*
    mv -fv ./"$filename".zip "$CSPROJDIR/../Package/"
done
