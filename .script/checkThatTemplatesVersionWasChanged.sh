#!/bin/bash

failed=0
SAVEIFS=$IFS
IFS=$'\n'
filesThatWereChanged=$(git diff origin/master --diff-filter=M --name-only)
IFS=$SAVEIFS
for (( i=0; i<${#filesthatwerechanged[@]}; i++ ))
    #Going over all the files that were changed in this PR
    #And making sure that in every file that its filename contains the word "Detection", the version was updated
    do
    	echo processing the file ${filesthatwerechanged[$i]}.
	if [[ "${filesthatwerechanged[$i]}" == *"Detections/"* || "${filesthatwerechanged[$i]}" == *"Analytic Rules/"* ]];
	then
		echo ${filesthatwerechanged[$i]} is a detection
		diffs=$(echo $(git diff origin/master -U0 --ignore-space-change ${filesthatwerechanged[$i]}))
		if [[ "$diffs" == *"version:"* ]];
		then
			echo "all good - the version was updated"
		else
			echo "You **did not** change the version in this file: ${filesthatwerechanged[$i]}."
			failed=1
		fi

	else
		echo "${filesthatwerechanged[$i]} is not a detection."		
    fi
done

exit $failed
