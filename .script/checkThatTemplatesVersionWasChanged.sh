#!/bin/bash

failed=0
red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`

filesThatWereChanged=$(echo $(git diff origin/master --name-only))
for file in $filesThatWereChanged
    #Going over all the files that were changed in this PR
    #And making sure that in every file that its filename contains the word "Detection", the version was updated
    do
    	echo processing the file $file.
	if [[ "$file" == *"Detection"* ]];
	then
		echo $file is a detection
		diffs=$(echo $(git diff origin/master -U0 $file))
		if [[ "$diffs" == *"version:"* ]];
		then
			echo "${green}all good - the version was updated${reset}"
		else
			echo "${red}You **did not** change the version in this file: $file.${reset}"
			failed=1
		fi

	else
		echo "${green}$file is not a detection.${reset}"		
    fi
done
exit $failed
