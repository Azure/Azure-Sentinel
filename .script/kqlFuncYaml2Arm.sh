#!/bin/bash

failed=0

parsersSchemas=(ASimDns ASimNetworkSession ASimWebSession)
for schema in ${parsersSchemas[@]}
	do  
		filesThatWereChanged=$(echo $(git diff origin/master  --name-only -- Parsers/$schema/))
		if [ "$filesThatWereChanged" = "" ]; then 
			echo No files were changed under Azure-Sentinel/Parsers/$schema/
		else
			echo Regenerate ARM templates under Azure-Sentinel/Parsers/$schema/ARM
			echo $filesThatWereChanged
			rm -rf Parsers//$schema/ARM
			python ASIM/dev/ASimYaml2ARM/KqlFuncYaml2Arm.py -m asim -d Parsers//$schema/ARM Parsers//$schema/Parsers
		fi
	done

exit $failed
