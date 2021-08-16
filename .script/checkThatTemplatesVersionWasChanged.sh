#!/bin/bash

filesThatWereChanged=$(echo $(git diff origin/master --name-only))
for file in $filesThatWereChanged
do
    echo processing the file $file that was changed
	if [[ "$file" == *"Detection"* ]];
	then
		echo $file is a detection
		diffs=$(echo $(git diff origin/master -U0 $file))
		if [[ "$diffs" == *"version:"* ]];
		then
			echo all good - the version was updated
		else
			echo did not change the version in this file: $file
		fi
		
	else
		echo $file is not a detection		
fi
done
