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

function log() {
	echo "$@"
	DATE=$(date)
	echo "$DATE" "$@" | sudo tee -a  /var/log/sapcon-update.log > /dev/null
}		

STARTPARAMS="$@"
#global
dockerimage="mcr.microsoft.com/azure-sentinel/solutions/sapcon"
sdkfileloc="/sapcon-app/inst/"
CONTAINERNAMES=()
test_logs="NO LOGS TO DISPLAY"


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
	--no-imageprune)
		NOIMAGEPRUNE=1
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
echo 'Microsoft Sentinel Solution for SAP agent update script.

-----Update All MS SAPcon instances----
This process will update the Microsoft Sentinel SAP agent to latest version.
'
# Parameter validation
if [ -n "$SDKFILELOC" ] && [ ! -f "$SDKFILELOC" ]; then
	log 'Invalid SDK path:'
	log "$SDKFILELOC"
	exit 1
fi

check_package docker
check_package "jq"

# Image selection
if [ $DEVMODE ]; then
	dockerimage=$(echo "$DEVURL" | awk -F: '{print $1}')
	acr=$(echo "$DEVURL" | awk -F/ '{print $1}')
	sudo docker login "$acr" -u "$DEVACRLOGIN" -p "$DEVACRPWD"
	tagver=$(echo "$DEVURL" | awk -F: '{print ":"$2}')
else
	dockerimage=mcr.microsoft.com/azure-sentinel/solutions/sapcon
fi

contlist=$(docker ps -a --format "{{.Names}}")
while IFS= read -r contname; do
	containerlabel=$(docker inspect "$contname" --format '{{ index .Config.Labels "com.visualstudio.msazure.image.build.repository.name"}}')
	if [ "$containerlabel" != "ASI-Sentinel4SAP" ]; then
		log "Skipping container $contname as it does not appear to be a Microsoft Sentinel Solution for SAP Agent"
		continue
	fi

	if [[ ! -z ${CONTAINERNAMES[*]} ]] && [[ ! ${CONTAINERNAMES[*]} =~ $contname ]]; then
		log "Skipping agent $contname as it is not specified in --containername list"
		continue
	fi

	log "Checking if upgrade is necessary for agent $contname"
	CLOUD=$(docker inspect "$contname" --format '{{index .Config.Labels "Cloud"}}')

	labelstring="--label Cloud=$CLOUD"
	if [ ! $DEVMODE ]; then
		if [ "$CLOUD" == 'public' ] || [ -z $CLOUD ]; then
			tag=':latest'
		elif [ "$CLOUD" == 'fairfax' ]; then
			tag=':ffx-latest'
			az cloud set --name "AzureUSGovernment" >/dev/null 2>&1
		elif [ "$CLOUD" == 'mooncake' ]; then
			tag=':mc-latest'
			az cloud set --name "AzureChinaCloud" >/dev/null 2>&1
		else
			log "Skipping container $contname as its Cloud label is not supported: $CLOUD"
			continue
		fi
		if [ $PREVIEW ]; then
			tagver="$tag-preview"
		else
			tagver=$tag
		fi
	fi

	sysfileloc=$(docker inspect "$contname" --format '{{ .Mounts }}'| awk 'NR==1 {print $2}')
	containerimage=$(docker inspect "$contname" --format '{{.Config.Image}}')
	containerreleaseid=$(docker inspect "$contname" --format '{{ index .Config.Labels "com.visualstudio.msazure.image.release.releaseid"}}')
	log "Agent $contname release id is $containerreleaseid"	

	log 'Starting Docker image Pull'
	docker pull "$dockerimage$tagver"
	imagereleaseid=$(docker inspect "$dockerimage$tagver" --format '{{ index .Config.Labels "com.visualstudio.msazure.image.release.releaseid"}}')
	if [ $? -eq 1 ]; then
		log 'There was an error pulling updated agent - please check network connection'
		exit 1
	fi
	log "Updated image: $dockerimage$tagver  release id: $imagereleaseid"

	# Update container if container image is not the same as the one in repo, or if force is set.
	# Update container if running a manual update, or if container has Auto Update flag set
	if [ "$imagereleaseid" == "$containerreleaseid" ] && [ ! $FORCE ]; then
		log "Agent image for agent $contname is identical to the one in the container registry. Agent release id $containerreleaseid, release id of image available in container registry: $imagereleaseid. Not updating this agent"
		continue
	elif [ "$containerreleaseid" -gt "$imagereleaseid" ] && [ ! $FORCE ]; then
		if [[ "$containerimage" == *"-preview"* ]] && [ ! $PREVIEW ]; then
			# Image is on preview, and no newer version is available
			log "Current agent is in preview branch, and release branch has an older build (current release id is $containerreleaseid, latest is $imagereleaseid). Not updating this agent"
		else
			log_update "Agent image for agent $contname is newer than the one in the container registry. Agent release id $containerreleaseid, release id of image available in container registry: $imagereleaseid. Not updating this agent"
		fi
		continue
	elif [ "$imagereleaseid" -gt "$containerreleaseid" ] || [ "$FORCE" == 1 ]; then	
		if [[ "$containerimage" == *"-preview"* ]] && [ ! $PREVIEW ] && [ "$imagereleaseid" -gt "$containerreleaseid" ]; then
			#Non-preview version of the image is newer than current
			log "Current agent is in preview branch, however a release branch has a newer build (current release id is $containerreleaseid, latest is $imagereleaseid). Switching agent to release branch"
		fi
		
		log "Inspecting $contname"

		if [ -z "$sysfileloc" ]; then
			log "Agent $contname cannot be updated - The config mount point is empty"
			exit 1
		fi
		if [ "${sysfileloc: -1}" != "/" ]; then
			sysfileloc="$sysfileloc/"
		fi
		read -r -a containervariables <<<$(docker inspect "$contname" --format '{{.Config.Env}}' | tr -d '[' | tr -d ']' | tr ' ' ' ')
		envstring=""
		for variable in "${containervariables[@]}"; do
			if [[ ! $variable == PATH=* ]] &&
				[[ ! $variable == LANG=* ]] &&
				[[ ! $variable == GPG_KEY=* ]] &&
				[[ ! $variable == PYTHON_VERSION=* ]] &&
				[[ ! $variable == PYTHON_PIP_VERSION=* ]] &&
				[[ ! $variable == PYTHON_SETUPTOOLS_VERSION=* ]] &&
				[[ ! $variable == PYTHON_GET_PIP_URL=* ]] &&
				[[ ! $variable == PYTHON_PATH=* ]] &&
				[[ ! $variable == PIPX_HOME=* ]] &&
				[[ ! $variable == PIPX_BIN_DIR=* ]] &&
				[[ ! $variable == NVM_DIR=* ]] &&
				[[ ! $variable == NVM_SYMLINK_CURRENT=* ]] &&
				[[ ! $variable == PYTHON_GET_PIP_SHA256=* ]]; then
				envstring+="-e $variable "
			fi
		done

		# Check if we have an agent guid already. if we don't have - generate and add to the envstring
		if [[ $envstring != *"SENTINEL_AGENT_GUID="* ]]; then
			envstring+="-e SENTINEL_AGENT_GUID=$(uuidgen) "
		fi
			
		ContainerNetworkSetting=$(docker inspect "$contname" --format '{{.Config.Labels.ContainerNetworkSetting}}')
		if [ "$ContainerNetworkSetting" == "<no value>" ]; then
			ContainerNetworkSetting=""
		fi
			
		RestartPolicy=$(docker inspect "$contname" --format '{{.HostConfig.RestartPolicy.Name}}')
			
		restartpolicystring="--restart $RestartPolicy"
		
		log "Agent $contname restart policy is set to $RestartPolicy"

		isRunning=$(docker inspect "$contname" --format='{{.State.Running}}')
		log "Agent $contname running state is $isRunning"
		isRestarting=$(docker inspect "$contname" --format='{{.State.Restarting}}')
		log "Agent $contname restarting state is $isRestarting"
		lastExitCode=$(docker inspect "$contname" --format='{{.State.ExitCode}}')
		log "Agent $contname last exit code is $lastExitCode"
		lastFinished=$(docker inspect "$contname" --format='{{.State.FinishedAt}}')
		log "Agent $contname last stop time is $lastFinished"
		lastStarted=$(docker inspect "$contname" --format='{{.State.StartedAt}}')
		log "Agent $contname last start time is $lastStarted"

		if [ "$isRunning" == "true" ] || [ "$isRestarting" == "true" ];  then
			log "Stopping agent $contname before update"
			docker stop "$contname" >/dev/null 2>&1
		fi

		mkdir -p /tmp/sapcon-update/ >/dev/null 2>&1
		sudo rm -rf "/tmp/sapcon-update/$contname" >/dev/null 2>&1
		mkdir "/tmp/sapcon-update/$contname" >/dev/null 2>&1

		#Extract SDK from old container, or use a newly supplied one
		if [ -n "$SDKFILELOC" ]; then
			mkdir -p "/tmp/sapcon-update/$contname/inst"
			cp "$SDKFILELOC" "/tmp/sapcon-update/$contname/inst/"
		else
			docker cp "$contname":$sdkfileloc "/tmp/sapcon-update/$contname/inst/"
		fi
		sdkfilename=$(ls -1r /tmp/sapcon-update/$contname/inst/nwrfc*.zip | head -n 1)

		if [ ! $NOTESTRUN ]; then
			# If test run is required
			testruncontainer="$contname-testrun"
			log "Creating agent $contname in test mode"
			docker create -v "$sysfileloc:/sapcon-app/sapcon/config/system" $envstring $ContainerNetworkSetting --name "$testruncontainer" $dockerimage$tagver --sapconinstanceupdate >/dev/null
			docker cp "$sdkfilename" "$testruncontainer":$sdkfileloc
			docker start "$testruncontainer" >/dev/null

			let timeelapsed=0
			dryruninprogress="true"
			log "Starting agent test run..."
			while [ "$dryruninprogress" == "true" ] && [ $timeelapsed -le 120 ]; do
				dryruninprogress=$(docker inspect --format='{{.State.Running}}' "$testruncontainer")
				if [ "$dryruninprogress" == "false" ]; then
					containerexitcode=$(docker container inspect --format '{{.State.ExitCode}}' "$testruncontainer")
					echo ""
					log "Agent test run finished. Exit code $containerexitcode"
					if [ "$containerexitcode" == 0 ]; then
						dryrunsuccess=1
					elif [ "$containerexitcode" == 5 ]; then
						echo ""
						log "Failed to connect to the SAP system"
						dryrunsuccess=0
						break
					elif [ "$containerexitcode" == 6 ]; then
						echo ""
						log "Failed to send heartbeat data to Azure Sentinel Workspace"
						dryrunsuccess=0
						break
					elif [ "$containerexitcode" == 7 ]; then
						echo ""
						log "Insufficient authorizations in SAP"
						dryrunsuccess=0
						break
					elif [ "$containerexitcode" == 8 ]; then
						echo ""
						log "Agent runtime error"
						dryrunsuccess=0
						break
					else
						echo ""
						log "Agent test run exited with code $containerexitcode"
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
				echo ""
				log "Agent is running after timeout period expired"
				dryrunsuccess=0
				docker stop "$testruncontainer" >/dev/null
			fi
			log "Test run finished, removing agent in test run mode"
            		test_logs=$(docker logs "$testruncontainer" --tail 70 2>&1)
			docker rm "$testruncontainer" >/dev/null
		else
			log "Creating new agent without test mode"
			dryrunsuccess=1
		fi
		if [ "$dryrunsuccess" == 1 ]; then
			echo ""
			log "Test run successful, removing old agent"
			docker rm "$contname" >/dev/null
		else
			echo ""
			log "Test run NOT successful, removing new agent, renaming the old agent to original name"
			log "----Agent debug logs START----"
			log "$test_logs"
			log "----Agent debug logs END----"
		fi
		if [ $dryrunsuccess == 1 ]; then
			log "Creating updated agent $contname"
			labelstring="--label Cloud=$CLOUD "
			docker create -v "$sysfileloc:/sapcon-app/sapcon/config/system" $envstring $labelstring $restartpolicystring $ContainerNetworkSetting --name "$contname" $dockerimage$tagver >/dev/null
			docker cp "$sdkfilename" "$contname":"$sdkfileloc"
		fi
		#Cleaning sapcon-update folder
		sudo rm -rf /tmp/sapcon-update >/dev/null 2>&1

		if [ "$isRunning" == "true" ] || [ "$isRestarting" == "true" ]; then
			log "Starting agent $contname"
			docker start "$contname" >/dev/null
		fi
	fi

done \
	<<<"$contlist"

# Clearing old images
if [ -z $NOIMAGEPRUNE ]; then
	log "$(docker image prune --filter "label=com.visualstudio.msazure.image.build.repository.name=ASI-Sentinel4SAP" -a -f)"	
fi
