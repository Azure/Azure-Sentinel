#!/usr/bin/env bash

set -e
set -x

rm -rf .python_packages

# Get the version of Python 3
PYTHON_VERSION=$(python3 --version 2>&1)

# Check if it contains "Python 3.11"
if [[ $PYTHON_VERSION == "Python 3.11"* ]]; then
    echo "Python 3.11 is being used."
else
    echo "Python 3.11 is NOT being used."
    exit 1
fi

python3 -m venv .python_packages
source .python_packages/bin/activate
pip install -r requirements.txt

cd .python_packages/lib
ln -s python3.11/site-packages site-packages
cd ../..

git checkout origin/master AbnormalSecurityConn.zip

zip -r AbnormalSecurityConn.zip SentinelFunctionsOrchestrator .python_packages/lib/site-packages requirements.txt 

git add AbnormalSecurityConn.zip