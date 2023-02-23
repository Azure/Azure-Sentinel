#!/bin/zsh
# Use IDE to publish to folder: bin/Release/net6.0/publish.bak
# then unzip the generated zip file to a temporary folder, and use kdiff3 to compare it with publish.bak.
# So as to test whether the zip file generated from CLI is identical to the one by IDE.
#
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

./zip.sh

UNZIP_DIR="./unzip.output/"

rm -fr "$UNZIP_DIR"
unzip ./Package/IncidentProducer.zip -d "$UNZIP_DIR"
kdiff3 "$UNZIP_DIR"  ./IncidentProducer/bin/Release/net6.0/publish.bak/

rm -fr "$UNZIP_DIR"
unzip ./Package/IncidentConsumer.zip -d "$UNZIP_DIR"
kdiff3 "$UNZIP_DIR"  ./IncidentConsumer/bin/Release/net6.0/publish.bak/

rm -fr "$UNZIP_DIR"
git checkout ./Package/*.zip
