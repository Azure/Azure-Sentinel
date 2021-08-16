#!/bin/bash

var=$(echo $(git diff origin/main -U0))

if [[ "$var" == *"version"* ]];
then
    echo "Changed the version of the template, nice!"
    exit 0
else
    echo "Hey there, you did not change the version of the template, please update the version of the template you changed."
    exit 1
fi
