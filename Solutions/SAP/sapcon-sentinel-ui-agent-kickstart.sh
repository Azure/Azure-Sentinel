#!/bin/bash

function log() {
	echo "$@"
	DATE=$(date)
	echo "$DATE" "$@" | sudo tee -a /var/log/sapcon-sentinel-ui-agent-kickstart.log > /dev/null 
}

function verlte() {
	[ "$1" = "$(echo -e "$1\n$2" | sort -V | head -n1)" ]
}

function verlt() {
	[ "$1" = "$2" ] && return 1 || verlte $1 $2
}


function install_package() {
	# $1 package name
	# $2 install command
	if ! which "$1" >/dev/null 2>&1; then
		log "Installing $1"
		if ! cmdresult=$(sudo $2 $1 2>&1); then
			log "Failed to install $1"
			log "$cmdresult"
			exit 1
		fi
	fi
}

# MODE is one of
# kvmi - Key Vault - Managed Identity
# kvsi - Key Vault - Supplied Identity

MODE="kvmi"
CONFIGPATH="/opt"
RESTARTPOLICY="--restart unless-stopped"
NETWORKSTRING=""
CLOUD="public"
UI_AGENT=""
UPDATEPOLICY='{ "auto_update" : true }'

while [[ $# -gt 0 ]]; do
	case $1 in
	--keymode)
		MODE="$2"
		shift 2
		;;
	--configpath)
		CONFIGPATH="$2"
		shift 2
		;;
	--sdk)
		SDKFILELOC="$2"
		SDKFILELOC="${SDKFILELOC/#\~/$HOME}"
		shift 2
		;;
	--network)
		NETWORKSTRING="--network $2"
		shift 2
		;;
	--appid)
		APPID="$2"
		shift 2
		;;
  	--hostnetwork)
		HOSTNETWORK=1
		shift 1
		;;
	--appsecret)
		APPSECRET="$2"
		shift 2
		;;
	--tenantid)
		TENANT="$2"
		shift 2
		;;
	--kvaultname)
		kv="$2"
		shift 2
		;;
	--noautorestart)
		RESTARTPOLICY=""
		shift
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
	--sapcryptolibpath)
		SAPCRYPTOLIBPATH="$2"
		SAPCRYPTOLIBPATH="${SAPCRYPTOLIBPATH/#\~/$HOME}"
		shift 2
		;;
	--http-proxy)
		HTTPPROXY="$2"
		shift 2
		;;
	--cloud)
		CLOUD="$2"
		shift 2
		;;
	--guid)
		GUID="$2"
		shift 2
		;;
	--ui-agent)
		UI_AGENT="-e UI_AGENT=True"
		shift 1
		;;
	--agent-name)
		AGENTNAME="$2"
		shift 2
		;;
	--preview)
		PREVIEW=1
		shift 1
		;;
	--script-debug)
		set -x
		shift 1
		;;
	-*)
		echo "Unknown option $1"
		echo "Valid options are"
		echo "--keymode [kvmi|kvsi]"
		echo "--configpath <path>"
		echo "--sdk <filename>"
		echo "--hostnetwork"
		echo "--network <network>"
		echo "--appid <guid>"
		echo "--appsecret <secret>"
		echo "--tenantid <guid>"
		echo "--agent-name <agent_name>"
		echo "--kvaultname <keyvaultname>"
		echo "--noautorestart"
		echo "--sapcryptolibpath <path to folder containing sap crypto lib and sapgenpse"
		echo "--http-proxy <proxy url>"
		echo "--preview"
		exit 1
		;;
	*)
		POSITIONAL_ARGS+=("$1") # save positional arg
		shift                   # past argument
		;;
	esac
done

# UI Agent validation
if [ -z "$UI_AGENT" ] || 
   [ -z "$GUID" ] || 
   [ -z "$AGENTNAME" ] || 
   [ -z "$kv" ] || 
   [ -z "$SDKFILELOC" ] || 
   ( [ "$MODE" != 'kvsi' ] && [ "$MODE" != 'kvmi' ] ) ||   
   ( [ "$MODE" == 'kvsi' ] && ( [ -z "$APPID" ] || [ -z "$APPSECRET" ] || [ -z "$TENANT" ] ) ) ||
   ( [ "$CLOUD" != 'public' ] && [ "$CLOUD" != 'fairfax' ] && [ "$CLOUD" != 'mooncake' ] ); then   
		log 'This script is intended exclusively for deploying Sentinel for SAP data connector using Azure UI-driven deployment. Do not run this script in standalone. For manual deployment, use the kickstart script available at https://aka.ms/sentinel4sapkickstart'
		exit 1
fi

if [ -n "$SAPCRYPTOLIBPATH" ]; then
	if [ ! -d "$SAPCRYPTOLIBPATH" ] || [ ! -f "$SAPCRYPTOLIBPATH/libsapcrypto.so" ] || [ ! -f "$SAPCRYPTOLIBPATH/sapgenpse" ]; then
		log 'Invalid SAP Crypto Lib path. Either target folder does not exist, or it does not contain libsapcrypto.so or sapgenpse'
		exit 1
	else
		USESNC=1
		SAPCRYPTOLIB="$SAPCRYPTOLIBPATH/libsapcrypto.so"
		SAPGENPSE="$SAPCRYPTOLIBPATH/sapgenpse"
	fi
fi

if [ ! -f "$SDKFILELOC" ]; then
	log 'Invalid SDK path:'
	log "$SDKFILELOC"
	exit 1
fi

# End of parameter validation
echo '
************************************************************
THIS INSTALLATION SCRIPT WILL USE ROOT ACCESS TO:

1. Download, install and configure the Microsoft Sentinel Solution for SAP agent
2. Add the current user to the docker group
3. Run the Microsoft Sentinel Solution for SAP agent as a docker container on the host

*************************************************************

-----Microsoft Sentinel Solution for SAP Agent deployment script----

Please review Microsoft Sentinel Solution for SAP deployment guide available at https://aka.ms/sentinel4sapdocs
'

#Globals
containername=sapcon
sysconf=systemconfig.ini
settingsjson=settings.json

os=$(awk </etc/os-release 'BEGIN { FS="=" } $1=="ID" {print $2}')
ver_id=$(awk </etc/os-release 'BEGIN { FS="=" } $1=="VERSION_ID" {print $2}' | awk '{print substr($0, 2, length($0) - 2) }')
id_like=$(awk </etc/os-release 'BEGIN { FS="=" } $1=="ID_LIKE" {print $2}')
log "Running on $os version $ver_id id $id_like"

#Installing prerequisites
if [ "$os" == "ubuntu" ]; then
	#Ubuntu
	log 'Updating package lists'
	sudo apt-get update >/dev/null
	install_package "jq" "apt install -y -qq"
	install_package "unzip" "apt install -y -qq"
	install_package "docker.io" "apt install -y -qq"
	if [ "$MODE" != "cfgf" ]; then
		log "Installing Azure CLI"
		curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash >/dev/null 2>&1
	fi

elif [ "$os" == '"rhel"' ]; then
	#RHEL
	log 'Updating package lists'
	sudo yum update -y --disablerepo='*' --enablerepo='*microsoft*' >/dev/null
	install_package "nc" "yum install -y"
	install_package "jq" "yum install -y"

	if [ "$MODE" != "cfgf" ]; then
		sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc >/dev/null
		echo -e "[azure-cli]\nname=Azure CLI\nbaseurl=https://packages.microsoft.com/yumrepos/azure-cli\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" | sudo tee /etc/yum.repos.d/azure-cli.repo >/dev/null
		log "Installing Azure CLI"
		sudo yum install azure-cli -y >/dev/null
	fi
	sudo yum install -y yum-utils >/dev/null
	sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo >/dev/null
	log "Installing Docker"
	sudo yum install docker-ce docker-ce-cli containerd.io -y >/dev/null
	sudo systemctl enable docker.service
	sudo systemctl start docker.service

elif [ "$os" == '"sles"' ]; then
	# SUSE
	log "Updating package lists"
	sudo zypper refresh >/dev/null
	log "Updating installed packages"
	sudo zypper update -y >/dev/null
	install_package "curl" "zypper install -y"
	install_package "jq" "zypper install -y"
	install_package "docker" "zypper install -y"
	sudo systemctl enable docker.service
	sudo systemctl start docker.service

	if [ "$MODE" != "cfgf" ]; then
		if ! rpm -qa | grep gpg-pubkey-be1229cf-5631588c >/dev/null; then
			sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc >/dev/null
			log "Adding Microsoft GPG key"
		fi
		if ! sudo zypper lr | grep "Azure CLI" >/dev/null; then
			sudo zypper addrepo --name 'Azure CLI' --check https://packages.microsoft.com/yumrepos/azure-cli azure-cli >/dev/null
			log "Adding Microsoft Azure CLI repository"
		fi
		if which az >/dev/null 2>&1; then
			#AZ is installed, check if it is out-of date version with compatibility issues
			azver=$(az version | jq '."azure-cli"')
			if verlte "2.33.1" "$azver"; then
				log "Installed version $azver is out of date, removing older version"
				sudo zypper rm -y --clean-deps azure-cli >/dev/null
				log "Installing Azure CLI"
				sudo zypper install -y --from azure-cli azure-cli >/dev/null
			fi
		else
			log "Installing Azure CLI"
			sudo zypper install -y --from azure-cli azure-cli >/dev/null
		fi
	fi
else
	log "OS version is not suppored. Supported OS: Ubuntu version 18.04 or higher, SLES version 15 or higher, or RHEL version 7.7 or higher"
	log "Current OS: $os"
	exit 1
fi

if [ $DEVMODE ]; then
	dockerimage=$(echo "$DEVURL" | awk -F: '{print $1}')
	acr=$(echo "$DEVURL" | awk -F/ '{print $1}')
	sudo docker login "$acr" -u "$DEVACRLOGIN" -p "$DEVACRPWD"
	tagver=$(echo "$DEVURL" | awk -F: '{print ":"$2}')
else
	dockerimage=mcr.microsoft.com/azure-sentinel/solutions/sapcon
	
	if [ "$CLOUD" == 'public' ]; then
		tagver=':latest'
	elif [ "$CLOUD" == 'fairfax' ]; then
		tagver=':ffx-latest'
		az cloud set --name "AzureUSGovernment" >/dev/null 2>&1
	elif [ "$CLOUD" == 'mooncake' ]; then
		tagver=':mc-latest'
		az cloud set --name "AzureChinaCloud" >/dev/null 2>&1
	fi

	if [ $PREVIEW ]; then
		tagver="$tagver-preview"
	fi
fi

# sudo groupadd docker
log "Creating group 'docker' and adding current user to 'docker' group"
sudo usermod -aG docker "$USER"

if [ "$MODE" == "kvmi" ]; then
	log "Validating Azure managed identity"
	az login --identity --allow-no-subscriptions >/dev/null 2>&1
	if [ ! $? -eq 0 ]; then
		log 'VM is not set with managed identity or the AZ client was not installed correctly.'
		log 'Set and grant relevant Key Vault permissions and make sure that Azure CLI is installed by running "az login"'
		log 'For more information check - https://docs.microsoft.com/cli/azure/install-azure-cli'
		exit 1
	fi
elif [ "$MODE" == "kvsi" ]; then
	log "Validating service principal identity"
	az login --service-principal -u "$APPID" -p "$APPSECRET" --tenant "$TENANT" --allow-no-subscriptions >/dev/null 2>&1
	if [ ! $? -eq 0 ]; then
		log "Logon with $APPID failed, please check application ID, secret and tenant ID. Ensure the application has been added as an enterprise application"
		exit 1
	fi
	az keyvault secret list --id "https://$kv.vault.azure.net/" >/dev/null 2>&1
	if [ ! $? -eq 0 ]; then
		log "Cannot connect to keyvault $kv. Make sure application $APPID has been granted privileges to the keyvault"
		exit 1
	fi
fi

log 'Deploying Microsoft Sentinel SAP data connector.'

log 'Starting Docker image pull'

sudo docker pull $dockerimage$tagver
if [ $? -eq 1 ]; then
	log 'Error downloading the Microsoft Sentinel SAP data connector.'
	exit 1
fi
log 'Latest Microsoft Sentinel data connector downloaded successfully.'
imagereleaseid=$(docker inspect "$dockerimage$tag" --format '{{ index .Config.Labels "com.visualstudio.msazure.image.release.releaseid"}}')
log "Downloaded data connector version $imagereleaseid" 

sysfileloc=$CONFIGPATH/$containername/$AGENTNAME/

sudo mkdir -p "$sysfileloc"
sudo chown "$USER" "$sysfileloc"
if [ ! $? -eq 0 ]; then
	log 'Error creating the local folder.'
	exit 1
fi

# If SNC is used, copy files required for SNC inside container mountpoint.
# Container init script looks for the specific location (config folder/sec) and specific filenames (client.crt, client.key, server.crt etc)
if [ $USESNC ]; then
	# Cleanup old data, if exists
	if [ -d "$sysfileloc"sec ]; then
		sudo rm -rf "$sysfileloc"sec
	fi
	sudo mkdir -p "$sysfileloc"sec
	sudo chown "$USER" "$sysfileloc"sec
	cp "$SAPCRYPTOLIB" "$sysfileloc"sec/libsapcrypto.so >/dev/null 2>&1
	cp "$SAPGENPSE" "$sysfileloc"sec/sapgenpse >/dev/null 2>&1
	chmod -R 600 "$sysfileloc"sec/* >/dev/null 2>&1
	chmod 700 "$sysfileloc"sec/libsapcrypto.so >/dev/null 2>&1
	chmod 700 "$sysfileloc"sec/sapgenpse >/dev/null 2>&1
	chmod 700 "$sysfileloc"sec >/dev/null 2>&1
	sudo chown root:root "$sysfileloc"sec >/dev/null 2>&1
fi

#Verifying SDK version only in case of non-fedora OS
if [ "$os" != "fedora" ]; then
	unzip -o "$SDKFILELOC" -d /tmp/ > /dev/null 2>&1
	sudo chmod +x -R /tmp/nwrfcsdk/lib/*.so
	SDKLOADRESULT=$(ldd /tmp/nwrfcsdk/lib/libsapnwrfc.so 2>&1)
	sdkok=$?
	rm -rf /tmp/nwrfcsdk
	if [ ! $sdkok -eq 0 ]; then
		log "Invalid SDK supplied. The error while attempting to load the SAP NetWeaver SDK:"
		log "$SDKLOADRESULT"
		log "Please rerun script supplying version of SAP NetWeaver SDK compatible with the current OS platform"
		exit 1
	fi
fi

#Building the container
containername="$containername-$AGENTNAME"
cmdparams=""
sudo docker inspect "$containername" >/dev/null 2>&1
if [ $? -eq 0 ]; then
	log 'Microsoft Sentinel SAP agent is already installed. The previous agent will be removed and replaced by the new version.'
	sudo docker stop "$containername" >/dev/null
	sudo docker container rm "$containername" >/dev/null
fi

if [ $USESNC ]; then
	cmdparams+=" -e SECUDIR=/sapcon-app/sapcon/config/system/sec/"
fi

if [ -n "$NETWORKSTRING" ]; then
	cmdparams+=" --label ContainerNetworkSetting=$NETWORKSTRING"
	cmdparams+=" $NETWORKSTRING"
fi

if [ -n "$HTTPPROXY" ]; then
	cmdparams+=" -e HTTP_PROXY=$HTTPPROXY -e HTTPS_PROXY=$HTTPPROXY"
fi

cmdparams+=" -e AZURE_KEY_VAULT_NAME=$kv"
cmdparams+=" -e SENTINEL_AGENT_GUID=$GUID"

cmdparams+=" --label Cloud=$CLOUD"

cmdparams+=" $RESTARTPOLICY"

cmdparams+=" $UI_AGENT"

if [ "$MODE" == "kvmi" ]; then
	log "Creating agent and configuring to use Azure Key vault and managed VM identity"
elif [ "$MODE" == "kvsi" ]; then
	log "Creating agent and configuring to use Azure Key vault and application authentication"
	cmdparams+=" -e AZURE_CLIENT_ID=$APPID -e AZURE_CLIENT_SECRET=$APPSECRET -e AZURE_TENANT_ID=$TENANT"
fi
if [ $HOSTNETWORK ]; then
	cmdparams+=" --network host "
fi
sudo docker create -v "$sysfileloc":/sapcon-app/sapcon/config/system $cmdparams --name "$containername" $dockerimage$tagver >/dev/null

log 'Created Microsoft Sentinel SAP agent '"$AGENTNAME"

sudo docker run --rm --entrypoint cat $dockerimage$tagver /sapcon-app/template/systemconfig-kickstart-blank.ini | sudo tee "$sysfileloc$sysconf" > /dev/null

if [ ! $? -eq 0 ]; then
	log 'Error accessing the local folder.'
	exit 1
fi

# #populate settings.json
echo $UPDATEPOLICY> "$sysfileloc$settingsjson"

log 'System information Has been Updated'

sudo docker cp "$SDKFILELOC" "$containername":/sapcon-app/inst/ >/dev/null
if [ $? -eq 0 ]; then
	log 'SDK archive was successfully updated'
else
	log 'Microsoft Sentinel data connector upgrade failed. The NetWeaver SDK could not be added to the image'
	exit 1
fi

sudo docker start "$containername" >/dev/null
if [ $? -eq 0 ]; then
	echo '
Microsoft Sentinel Solution for SAP agent was started - quick reference for future steps:
View logs: docker logs '"$containername"'
View logs continuously: docker logs -f '"$containername"'
Stop the connector: docker stop '"$containername"'
Start the connector: docker start '"$containername"'
The process has been successfully completed, thank you!'
else
	log 'Could not start Microsoft Sentinel Solution for SAP agent'
	exit 1
fi

newgrp docker

