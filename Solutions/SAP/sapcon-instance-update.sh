#!/bin/bash

function pause() {
	if [ ! "$CONFIRMALL" ]; then
		read -r -p "$*"
	fi
}

function check_package() {
	if ! which "$1" >/dev/null 2>&1; then
		echo "Binary $1 not found"
		echo "Please install $1 and run the upgrade script again"
		exit 1
	fi
}

#global
dockerimage=mcr.microsoft.com/azure-sentinel/solutions/sapcon
sdkfileloc=/sapcon-app/inst/
CONTAINERNAMES=()

while [[ $# -gt 0 ]]; do
	case $1 in
	--confirm-all-prompts)
		CONFIRMALL=1
		shift 1
		;;
	--no-testrun)
		NOTESTRUN=1
		shift 1
		;;
	--sdk)
		SDKFILELOC="$2"
		SDKFILELOC="${SDKFILELOC/#\~/$HOME}"
		shift 2
		;;
	--containername)
		CONTAINERNAMES+=("$2")
		shift 2
		;;
	--devmode)
		DEVMODE=1
		shift 1
		;;
	--dev-acr)
		DEVURL="$2"
		shift 2
		;;
	--dev-acr-login)
		DEVACRLOGIN="$2"
		shift 2
		;;
	--dev-acr-pwd)
		DEVACRPWD="$2"
		shift 2
		;;
	--preview)
		PREVIEW=1
		shift 1
		;;
	--force)
		FORCE=1
		shift 1
		;;
	--script-debug)
		set -x
		shift 1
		;;
	-*)
		echo "Unknown option $1"
		echo "Valid options are"
		echo "--confirm-all-prompts"
		echo "--preview"
		echo "--script-debug"
		echo "--no-testrun"
		echo "--sdk <filepath>"
		echo "--containername <containername> [--containername <containername>]..."
		exit 1
		;;
	*)
		POSITIONAL_ARGS+=("$1") # save positional arg
		shift                   # past argument
		;;
	esac
done
#Copyright (c) Microsoft Corporation. All rights reserved.
echo 'Microsoft Azure Sentinel SAP Continuous Threat Monitoring.
SAP ABAP Logs Connector -  Preview

Copyright (c) Microsoft Corporation. 
You may use this preview software internally and only in accordance with the Azure preview terms, located at https://azure.microsoft.com/support/legal/preview-supplemental-terms/  

Microsoft reserves all other rights
****

-----Update All MS SAPcon instances----
This process will download the latest version of Sentinel SAP Connector, Updates current image and containers. A currently running version of the instance will be stopped and automatically start after the process.
In order to process you will need the following prerequisites: 
'
# Parameter validation
if [ -n "$SDKFILELOC" ] && [ ! -f "$SDKFILELOC" ]; then
	echo 'Invalid SDK path'
	exit 1
fi
# Image selection
if [ $DEVMODE ]; then
	dockerimage=$(echo "$DEVURL" | awk -F: '{print $1}')
	acr=$(echo "$DEVURL" | awk -F/ '{print $1}')
	sudo docker login "$acr" -u "$DEVACRLOGIN" -p "$DEVACRPWD"
	tagver=$(echo "$DEVURL" | awk -F: '{print ":"$2}')
else
	dockerimage=mcr.microsoft.com/azure-sentinel/solutions/sapcon
	if [ $PREVIEW ]; then
		tagver=":latest-preview"
	else
		tagver=":latest"
	fi
fi

check_package docker
check_package jq

echo 'Starting Docker image Pull'
docker pull $dockerimage$tagver
if [ $? -eq 1 ]; then
	echo 'There is an error with the docker image - please Check network connection'
	exit 1
fi
pause '
Image has been downloaded - Press <Enter> key to continue with the Update'
repoimageid=$(docker inspect "$dockerimage$tagver" --format '{{.Id}}')

contlist=$(docker container ls -a | awk 'NR!=1 {print $1}')
while IFS= read -r contid; do
	containerlabel=$(docker inspect "$contid" | jq '.[].Config.Labels."com.visualstudio.msazure.image.build.repository.name"')
	if [ "$containerlabel" == '"ASI-Sentinel4SAP"' ]; then
		contimg=$(docker inspect --format='{{.Image}}' "$contid")
		contname=$(docker inspect --format '{{.Name}}' "$contid")
		contname="${contname:1}"
		if [[ -z ${CONTAINERNAMES[*]} ]] || [[ ${CONTAINERNAMES[*]} =~ $contname ]]; then
			echo "Checking if upgrade is necessary for container $contname"
			if [[ ! "$contimg" == "$repoimageid" ]] || [[ $FORCE == 1 ]]; then
				echo "Updating $contname"
				if [ -n "$contid" ]; then
					sysfileloc=$(docker inspect -f '{{ .Mounts }}' $contname | awk 'NR==1 {print $2}')
					if [ -z "$sysfileloc" ]; then
						echo "Container $contname cannot be updated - The mount point is empty"
						exit 1
					fi
					last=${sysfileloc: -1}

					if [ "$last" != "/" ]; then
						sysfileloc="$sysfileloc/"
					fi

					read -r -a containervariables <<<"$(docker inspect $contname -f '{{.Config.Env}}' | tr -d '[' | tr -d ']' | tr ' ' ' ')"
					envstring=""
					for variable in "${containervariables[@]}"; do
						if [[ ! $variable == PATH=* ]] &&
							[[ ! $variable == LANG=* ]] &&
							[[ ! $variable == GPG_KEY=* ]] &&
							[[ ! $variable == PYTHON_VERSION=* ]] &&
							[[ ! $variable == PYTHON_PIP_VERSION=* ]] &&
							[[ ! $variable == PYTHON_SETUPTOOLS_VERSION=* ]] &&
							[[ ! $variable == PYTHON_GET_PIP_URL=* ]] &&
							[[ ! $variable == PYTHON_GET_PIP_SHA256=* ]]; then
							envstring+="-e $variable "
						fi
					done
					# Check if we have an agent guid already. if we don't have - generate and add to the envstring
					if [[ $envstring != *"SENTINEL_AGENT_GUID="* ]]; then
						envstring+="-e SENTINEL_AGENT_GUID=$(uuidgen) "
					fi

					isRunning=$(docker inspect --format='{{.State.Running}}' "$contname")
					if [ "$isRunning" == "true" ]; then
						docker stop "$contname"
					fi
					mkdir -p /tmp/sapcon-update/ >/dev/null 2>&1
					sudo rm -rf "/tmp/sapcon-update/$contname" >/dev/null 2>&1
					mkdir "/tmp/sapcon-update/$contname" >/dev/null 2>&1

					#renaming the container, creating a new test container
					oldname="$contname-OLD"
					docker container rename "$contname" "$oldname" >/dev/null

					#Extract SDK from old container, or use a newly supplied one
					if [ -n "$SDKFILELOC" ]; then
						mkdir -p "/tmp/sapcon-update/$contname/inst"
						cp "$SDKFILELOC" "/tmp/sapcon-update/$contname/inst/"
					else
						docker cp "$oldname":$sdkfileloc "/tmp/sapcon-update/$contname"
					fi
					sdkfilename=$(ls -1r /tmp/sapcon-update/$contname/inst/nwrfc*.zip | head -n 1)

					if [ ! $NOTESTRUN ]; then
						# If test run is required
						docker create -v "$sysfileloc:/sapcon-app/sapcon/config/system" $envstring --name "$contname" $dockerimage$tagver --sapconinstanceupdate >/dev/null

						docker cp "$sdkfilename" "$contname":$sdkfileloc
						docker start "$contname" >/dev/null

						let timeelapsed=0
						dryruninprogress="true"
						echo -n "Starting container test run..."
						while [ "$dryruninprogress" == "true" ] && [ $timeelapsed -le 120 ]; do
							dryruninprogress=$(docker inspect --format='{{.State.Running}}' "$contname")
							if [ "$dryruninprogress" == "false" ]; then
								containerexitcode=$(docker container inspect --format '{{.State.ExitCode}}' "$contname")
								printf "\nContainer dry run exited. Exit code $containerexitcode"
								if [ "$containerexitcode" == 0 ]; then
									dryrunsuccess=1
									docker rm "$contname" >/dev/null
									docker create -v "$sysfileloc:/sapcon-app/sapcon/config/system" $envstring --name "$contname" $dockerimage$tagver >/dev/null
									docker cp $sdkfilename "$contname":"$sdkfileloc"
								elif [ "$containerexitcode" == 7 ]; then
									printf "\nInsufficient authorizations in SAP"
									dryrunsuccess=0
									break
								elif [ "$containerexitcode" == 8 ]; then
									printf "\nContainer runtime error"
									dryrunsuccess=0
									break
								else
									printf "\nContainer exited with code $containerexitcode"
									dryrunsuccess=0
									break
								fi
							fi
							sleep 1
							let timeelapsed=timeelapsed+1
							echo -n "."
						done
						if [ "$dryruninprogress" == "true" ]; then
							# container did not exit after 60 seconds
							printf "\nContainer is running after timeout period expired"
							docker stop "$contname" >/dev/null
						fi

						if [ "$dryrunsuccess" == 1 ]; then
							printf "\nTest run successful, removing old container"
							docker rm "$oldname" >/dev/null
						else
							printf "\nTest run NOT successful, removing new container, renaming the old container to original name"
							echo "----Container debug logs START----"
							docker logs "$contname"
							echo "----Container debug logs END----"
							docker rm "$contname" >/dev/null
							docker rename "$oldname" "$contname" >/dev/null
						fi
					else
						docker create -v "$sysfileloc:/sapcon-app/sapcon/config/system" $envstring --name "$contname" $dockerimage$tagver >/dev/null
						docker cp "$sdkfilename" "$contname":"$sdkfileloc"
						docker rm "$oldname"
					fi
					sudo rm -rf /tmp/sapcon-update >/dev/null 2>&1
				fi
				if [ "$isRunning" == "true" ]; then
					echo "Starting container $contname"
					docker start "$contname" >/dev/null
				fi
			else
				echo "Container image for container $contname is identical to the one in the repo"
			fi
		else
			echo "Skipping container $contname as it is not specified in --containername list"
		fi
	else
		echo "Skipping container id $contid as it does not appear to be a sapcon container"
	fi
done \
	<<<"$contlist"
