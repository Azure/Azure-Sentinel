#!/bin/bash

function log_update() {	
	echo "$@"
	DATE=$(date)
	echo "$DATE" "$@" | sudo tee -a /var/log/sapcon-sentinel-auto-update.log > /dev/null 
}

function log_register() {		
	echo "$@"
	DATE=$(date)
	echo "$DATE" "$@" | sudo tee -a /var/log/sapcon-sentinel-register-autoupdate.log > /dev/null 
}

function check_package() {
	if ! which "$1" >/dev/null 2>&1; then
		echo "Binary $1 not found"
		echo "Please install $1 and run the upgrade script again"
		exit 1
	fi
}

function register_auto_update() {
	if [ ! -f "/etc/logrotate.d/sapcon-sentinel-auto-update" ]; then
		log_register 'Create logrotate configuration: /etc/logrotate.d/sapcon-sentinel-auto-update'
		echo '/var/log/sapcon-update.log
/var/log/sapcon-sentinel-auto-update.log
/var/log/sapcon-sentinel-register-autoupdate.log {
	su root root
	missingok
	notifempty
	size 10M
	rotate 7
	create 0644 root root
	nocompress
}' | sudo tee -a "/etc/logrotate.d/sapcon-sentinel-auto-update" > /dev/null
	fi
	
	sudo logrotate /etc/logrotate.d/sapcon-sentinel-auto-update

	UPDATEPOLICY='{ "auto_update" : true }'	
	FREQUENCY="daily"
	CRONPATH="/etc/cron.$FREQUENCY/sapcon-update"
	AUTOUPDATESCRIPT="sapcon-sentinel-auto-update.sh"	

	echo '
************************************************************
THIS SCRIPT WILL USE ROOT ACCESS TO:

1. Download the registration for auto update of Microsoft Sentinel Solution for SAP agent
2. Schedule Cron Job of auto update
3. Create logrotate configuration in order to limit the memory consumption in the log files of the automatic update process

*************************************************************

-----Registration for auto update of Microsoft Sentinel Solution for SAP Agent deployment script----
'

	contlist=$(docker ps -a --format "{{.Names}}")
	while IFS= read -r contname; do
		containerlabel=$(docker inspect "$contname" --format '{{ index .Config.Labels "com.visualstudio.msazure.image.build.repository.name"}}')
		if [ "$containerlabel" != "ASI-Sentinel4SAP" ]; then
		log_register "Skipping container $contname as it does not appear to be a Microsoft Sentinel Solution for SAP agent"
			continue
		fi

		if [[ ! -z ${CONTAINERNAMES[*]} ]] && [[ ! ${CONTAINERNAMES[*]} =~ $contname ]]; then
			log_register "Skipping agent $contname as it is not specified in --containername list"
			continue
		fi

		log_register "Flag $contname for auto-update"

		sysfileloc=$(docker inspect "$contname" --format '{{ .Mounts }}'| awk 'NR==1 {print $2}')
		settingsjson=$sysfileloc/settings.json
		
		# Populate settings.json	
		if [ -f "$settingsjson" ]; then
			sudo chmod --reference "$0" "$settingsjson"
			sudo chown --reference "$0" "$settingsjson"
			sudo sync "$settingsjson"
			if [ ! -s "$settingsjson" ]; then
				echo $UPDATEPOLICY> "$settingsjson"
			else
				echo "$(jq '.auto_update = true' "$settingsjson")" > "$settingsjson"
			fi	
		else
			echo $UPDATEPOLICY> "$settingsjson"
		fi

	done \
		<<<"$contlist"

	# Set cron scheduling
	sudo cp "$0" "/tmp/$AUTOUPDATESCRIPT"
	sudo chmod --reference "$0" "/tmp/$AUTOUPDATESCRIPT"
	sudo chown --reference "$0" "/tmp/$AUTOUPDATESCRIPT"
	sudo sync "/tmp/$AUTOUPDATESCRIPT"
	sudo mkdir -p /opt/sapcon/
	sudo mv "/tmp/$AUTOUPDATESCRIPT" "/opt/sapcon/$AUTOUPDATESCRIPT"
	sudo chmod +x "/opt/sapcon/$AUTOUPDATESCRIPT"

	log_register "Scheduling $FREQUENCY update job as $CRONPATH"
	echo "#!/bin/bash" | sudo tee "$CRONPATH" > /dev/null	
	echo "/opt/sapcon/$AUTOUPDATESCRIPT --update-mode" | sudo tee -a "$CRONPATH" > /dev/null
	sudo chmod +x $CRONPATH

	
}

function update_agents() {
	sudo logrotate /etc/logrotate.d/sapcon-sentinel-auto-update

	log_update '-----Start update Microsoft Sentinel Solution for SAP Agents-----'
	settingsjson=settings.json
	contlist=$(docker ps -a --format "{{.Names}}")
	containernames=""

	log_update 'Scan for Microsoft Sentinel Solution for SAP Agents'

	while IFS= read -r contname; do
		containerlabel=$(docker inspect "$contname" --format '{{ index .Config.Labels "com.visualstudio.msazure.image.build.repository.name"}}')
		if [ "$containerlabel" != "ASI-Sentinel4SAP" ]; then
			log_update "Skipping container $contname as it does not appear to be a Microsoft Sentinel Solution for SAP Agent"
			continue
		fi

		sysfileloc=$(docker inspect "$contname" --format '{{ .Mounts }}'| awk 'NR==1 {print $2}')

		if [ ! -f "$sysfileloc/$settingsjson" ]; then
			log_update "Skipping container $contname as it is not set for auto-update"
			continue
		fi

		AutoUpdateFlag=$(cat "$sysfileloc/$settingsjson" | jq '."auto_update"')

		if [ "$AutoUpdateFlag" != "true" ]; then
			log_update "Skipping container $contname as it is not set for auto-update"
			continue
		fi

		if [ ! "$SKIPIMAGEPULL" ]; then
			CLOUD=$(docker inspect "$contname" --format '{{index .Config.Labels "Cloud"}}')

			dockerimage=mcr.microsoft.com/azure-sentinel/solutions/sapcon

			if [ "$CLOUD" == 'public' ] || [ -z $CLOUD ]; then
				tagver=':latest'
			elif [ "$CLOUD" == 'fairfax' ]; then
				tagver=':ffx-latest'
				az cloud set --name "AzureUSGovernment" >/dev/null 2>&1
			elif [ "$CLOUD" == 'mooncake' ]; then
				tagver=':mc-latest'
				az cloud set --name "AzureChinaCloud" >/dev/null 2>&1
			else
				log_update "Skipping container $contname as its Cloud label is not supported: $CLOUD"
				continue
			fi

			log_update 'Starting Docker image Pull'
			docker pull "$dockerimage$tagver"
			if [ $? -eq 1 ]; then
				log_update 'There was an error pulling updated agent - please check network connection'
				exit 1
			fi
			SKIPIMAGEPULL=1
		fi

		containernames+="--containername $contname "

	done \
		<<<"$contlist"

	if [ "$containernames" != "" ]; then
		log_update "Extracting newer update script from the updated agent image"
		sudo docker run --rm --entrypoint cat $dockerimage$tagver /sapcon-app/sapcon-instance-update.sh | sudo tee /tmp/sapcon-instance-update.sh > /dev/null
		sudo mv /tmp/sapcon-instance-update.sh /opt/sapcon/
		sudo chmod +x /opt/sapcon/sapcon-instance-update.sh

		/opt/sapcon/sapcon-instance-update.sh --confirm-all-prompts $containernames
	fi
}

check_package "jq"

CONTAINERNAMES=()

while [[ $# -gt 0 ]]; do
	case $1 in
	--containername)
		CONTAINERNAMES+=("$2")
		shift 2
		;;
	--update-mode)
		UPDATEMODE=1
		shift 1
		;;
	--script-debug)
		set -x
		shift 1
		;;
	-*)
		echo "Unknown option $1"
		echo "Valid options are"		
		echo "--containername <containername> [--containername <containername>]..."
		exit 1
		;;
	*)
		POSITIONAL_ARGS+=("$1") # save positional arg
		shift                   # past argument
		;;
	esac
done

if [ $UPDATEMODE ]; then
	update_agents
else
	register_auto_update
fi
