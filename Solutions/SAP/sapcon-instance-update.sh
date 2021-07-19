#!/bin/bash
#Copyright (c) Microsoft Corporation. All rights reserved.
echo 'Microsoft Azure Sentinel SAP Continuous Threat Monitoring.
SAP ABAP Logs Connector - Limited Private Preview

Copyright (c) Microsoft Corporation. This preview software is Microsoft Confidential, and is subject to your Non-Disclosure Agreement with Microsoft. 
You may use this preview software internally and only in accordance with the Azure preview terms, located at https://azure.microsoft.com/support/legal/preview-supplemental-terms/  

Microsoft reserves all other rights
****'
function pause(){
   read -p "$*"
}


#global
dockerimage=mcr.microsoft.com/azure-sentinel/solutions/sapcon
tagver=":latest-preview"
olddockerimage=sentinel4sapprivateprview.azurecr.io/sapcon
containername=sapcon
sysconf=systemconfig.ini
acr=sentinel4sapprivateprview.azurecr.io
sdkfileloc=/sapcon-app/inst/

echo '
-----Update All MS SAPcon instances----
This process will download the latest version of Sentinel SAP Connector, Updates current image and containers. A currently running version of the instance will be stopped and automatically start after the process.
In order to process you will need the following prerequisites: 
'

echo 'Starting Docker image Pull'
docker pull $dockerimage$tagver
if [ $? -eq 1 ];
then 
	echo 'There is an error with the docker image - please Check network connection'
	exit 1
fi
pause '
Image has been downloaded - Press <Enter> key to continue with the Update'

contlist=$(docker container ls -a | awk 'NR!=1 {print $1}')

while IFS= read -r contid
do	
	contimg=$(docker inspect --format='{{.Config.Image}}' $contid)
	contname=$(docker ps -a --filter id=$contid --format '{{.Names}}')
    
	if [[ "$contimg" = *"$dockerimage"* ]] || [[ "$contimg" = *"$olddockerimage"* ]]
	then
		echo ' '		
		echo Updating $contname...
		if [  ! -z $contid ]
		then
			sysfileloc=$(docker inspect -f '{{ .Mounts }}' $contname | awk 'NR==1 {print $2}')
			if [  ! -z $sysfileloc ]
			then
				last=${sysfileloc: -1}

				if [ "$last" != "/" ];
				then
					sysfileloc="$sysfileloc/"
				fi
				
				contstate=$(docker inspect --format='{{.State.Running}}' $contname )
				
				# pause 'press enter'
				if [ $contstate == "false" ]
				then
						docker cp $contname:$sdkfileloc $(pwd)
						docker container rm $contname >/dev/null
						docker create -v $sysfileloc:/sapcon-app/sapcon/config/system --name $contname $dockerimage$tagver >/dev/null
						docker cp "$(pwd)/inst/" $contname:/sapcon-app/ >/dev/null
						echo 'Container "'"$contname"'" was updated - please start the app by running "docker start '"$contname"'"'
						echo ''
				else
					docker cp $contname:$sdkfileloc $(pwd)
					docker stop $contname  >/dev/null
					docker container rm $contname  >/dev/null
					docker create -v $sysfileloc:/sapcon-app/sapcon/config/system --name $contname $dockerimage$tagver  >/dev/null
					docker cp "$(pwd)/inst/" $contname:/sapcon-app/  >/dev/null
					docker start $contname >/dev/null
					echo 'Container "'"$contname"'" was updated'
					echo ''
				fi
			else
				echo 'Container "'"$contname"'" cannot be updated - The mount point is empty'
				echo ' '
			fi
		else
			echo ''
		fi
		
	fi 	 
done <<< "$contlist"
