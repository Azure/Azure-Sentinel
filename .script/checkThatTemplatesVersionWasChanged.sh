#!/bin/bash

failed=0

filesThatWereChanged=$(echo $(git diff origin/master --diff-filter=M --name-only))
for file in $filesThatWereChanged
    #Going over all the files that were changed in this PR
    #And making sure that in every file that its filename contains the word "Detection", the version was updated
    do
    	echo processing the file $file.
	if [[ "$file" == *"Detections/"* ]];
	then
		echo $file is a detection
		diffs=$(echo $(git diff origin/master -U0 --ignore-space-change $file))
		if [[ "$diffs" == *"version:"* ]];
		then
			echo "all good - the version was updated"
		else
			echo "You **did not** change the version in this file: $file."
			failed=1
		fi

	else
		echo "$file is not a detection."		
    fi
done

exit $failed
