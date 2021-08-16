#!/bin/bash

var=$(echo $(git diff origin/master -U0))

if [[ "$var" == *"version:"* ]];
then
    echo "Changed the version of the template, nice!"
    exit 0
else
    echo "There are one or more templates that were modified and their version was not updated. Please update the version of the template(s) you changed."
    exit 1
fi
