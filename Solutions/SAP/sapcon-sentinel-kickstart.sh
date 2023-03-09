#!/bin/bash

function verlte() {
	[ "$1" = "$(echo -e "$1\n$2" | sort -V | head -n1)" ]
}

function verlt() {
	[ "$1" = "$2" ] && return 1 || verlte $1 $2
}

function read_password() {
	varname="$1"
	while [ -z "${!varname}" ]; do
		echo -n "Enter value for $2: " >$(tty)
		unset CHARCOUNT
		stty -echo
		CHARCOUNT=0
		unset PASSWORD
		unset CHAR
		unset PROMPT
		while IFS= read -p "$PROMPT" -r -s -n 1 CHAR; do
			# Enter - accept password
			if [[ $CHAR == $'\0' ]]; then
				break
			fi
			# Backspace
			if [[ $CHAR == $'\177' ]]; then
				if [ $CHARCOUNT -gt 0 ]; then
					CHARCOUNT=$((CHARCOUNT - 1))
					PROMPT=$'\b \b'
					PASSWORD="${PASSWORD%?}"
				else
					PROMPT=''
				fi
			else
				CHARCOUNT=$((CHARCOUNT + 1))
				PROMPT='*'
				PASSWORD+="$CHAR"
			fi
		done
		stty echo
		echo ""
		eval "$1"='$PASSWORD'
		if [ -z "${!varname}" ]; then
			echo "Invalid value supplied for $1. Value cannot be empty. Please try again" >$(tty)
		fi
	done
}

function read_value() {
	varname="$1"
	while [ -z "${!varname}" ]; do
		read -r -p "Enter $2: " varvalue
		if [ -z "$varvalue" ]; then
			echo "Supplied value for $2 is empty. Please try again." >$(tty)
		fi
		eval "$1"='$varvalue'
	done
}

function pause() {
	if [ ! "$CONFIRMALL" ]; then
		read -r -p "$*"
	fi
}

function install_package() {
	# $1 package name
	# $2 install command
	if ! which "$1" >/dev/null 2>&1; then
		echo "Installing $1"
		if ! cmdresult=$(sudo $2 $1 2>&1); then
			echo "Failed to install $1"
			echo "$cmdresult"
			exit 1
		fi
	fi
}

# MODE is one of
# kvmi - Key Vault - Managed Identity
# kvsi - Key Vault - Supplied Identity
# cfgf - Config File

# CONNECTIONMODE is one of
# abap
# mserv

containers=(
  "DGT d6ee1cdf-b728-46f4-9f0b-31e69709afba"
  "PZ0 000 d820db5b-ebb4-4d99-a03f-27d46914272e"
  "PG0 000 6dbf5698-6ea6-48aa-af57-ae8550066b35"
  "PA0 000 505b7f4d-b50c-4f7e-9a2e-6675a0dfb094"
  "P90 000 4be294d7-ef3d-404b-8577-a022e3f2622d"
  "P20 000 29b08227-5c70-4e18-91af-6a7b8eb9e1bc"
  "P10 000 94ba5d6d-6170-4903-a254-b9123143a98e"
  "DZ0 000 d5722834-d1a8-4800-8de9-5876f2b39f68"
  "DG9 000 d8b93965-1822-4f05-a744-7676b2165e92"
  "DG0 000 f01f2018-bba1-4aba-ae08-90e42219a01b"
  "D20 000 d073c785-ab76-4a60-bffc-d8ab0bfcd812"
  "D19 000 c005a8b3-ed15-4b97-9a83-b1871bc05cfd"
  "D10 000 c803745b-ec64-43db-ae9f-9c0417349a6e"
  "DA0 000 f78773d9-b60a-4679-805d-e4f5845bdb8a"
  "P10 700 815dc8de-359f-4ba9-8512-a1bb6abee7bb"
  "D10 700 a716eb31-54b7-4340-8d72-2896c626177a"
  "PA0 9b698a72-c5a8-4869-9c53-0ce3b09fb95d"
  "PZ0 9686913d-205c-4b84-b12a-6a162538e632"
  "PG0 91488ed5-ed2e-48bb-8fff-9916c00d882a"
  "P20 dcd79624-b8d6-4212-8acf-21ea05ac212b"
  "P10 d9c308df-dec4-4460-94d1-e0ee3ef87d0f"
  "P90 4500fcc0-22fe-4e01-aecb-221a5133d2ef"
  "D20 e9093650-8bfd-430b-a6c0-885e4d400a5b"
  "DZ0 f45be9fd-f1d2-4bef-9e84-e5a49cdcb3a8"
  "D19 c66eccaf-931b-47e5-95a6-306646c64d6e"
  "DG0 5422a744-ab6d-4410-8de9-8b9c9892c21b"
  "DG9 c1a01153-3baf-4399-b44d-b2495ee18d09"
  "D10 ec0a0c64-474b-47fd-8cff-49d9611969f9"
  "DA0 ac5fb83c-31ef-46c2-8430-85116093bab9"
)



MODE="kvmi"
CONNECTIONMODE="abap"
CONFIGPATH="/home/LocalAdmin"
TRUSTEDCA=()
CLOUD='public'

while [[ $# -gt 0 ]]; do
	case $1 in
	--connectionmode)
		CONNECTIONMODE="$2"
		shift 2
		;;
	--abapserver)
		ABAPSERVER="$2"
		shift 2
		;;
	--systemnr)
		SYSTEMNR="$2"
		shift 2
		;;
	--sid)
		SID="$2"
		shift 2
		;;
	--clientnumber)
		CLIENTNUMBER="$2"
		shift 2
		;;
	--messageserverhost)
		MESSAGESERVERHOST="$2"
		shift 2
		;;
	--messageserverport)
		MESSAGESERVERPORT="$2"
		shift 2
		;;
	--logongroup)
		LOGONGROUP="$2"
		shift 2
		;;
	--sapusername)
		uservar="$2"
		shift 2
		;;
	--sappassword)
		passvar="$2"
		shift 2
		;;
	--sdk)
		SDKFILELOC="$2"
		SDKFILELOC="${SDKFILELOC/#\~/$HOME}"
		shift 2
		;;
	--appid)
		APPID="$2"
		shift 2
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
	--loganalyticswsid)
		logwsid="$2"
		shift 2
		;;
	--loganalyticskey)
		logpubkey="$2"
		shift 2
		;;
	--use-snc)
		USESNC=1
		shift
		;;
	--cryptolib)
		SAPCRYPTOLIB="$2"
		SAPCRYPTOLIB="${SAPCRYPTOLIB/#\~/$HOME}"
		shift 2
		;;
	--sapgenpse)
		SAPGENPSE="$2"
		SAPGENPSE="${SAPGENPSE/#\~/$HOME}"
		shift 2
		;;
	--client-cert)
		CLIENTCERT="$2"
		CLIENTCERT="${CLIENTCERT/#\~/$HOME}"
		shift 2
		;;
	--client-key)
		CLIENTKEY="$2"
		CLIENTKEY="${CLIENTKEY/#\~/$HOME}"
		shift 2
		;;
	--cacert)
		ca="$2"
		ca="${ca/#\~/$HOME}"
		TRUSTEDCA+=("$ca")
		shift 2
		;;
	--client-pfx)
		CLIENTPFX="$2"
		CLIENTPFX="${CLIENTPFX/#\~/$HOME}"
		shift 2
		;;
	--client-pfx-passwd)
		CLIENTPFXPWD="$2"
		CLIENTPFXPWD="${CLIENTPFXPWD/#\~/$HOME}"
		shift 2
		;;
	--server-cert)
		SERVERCERT="$2"
		SERVERCERT="${SERVERCERT/#\~/$HOME}"
		shift 2
		;;
	--http-proxy)
		HTTPPROXY="$2"
		;;
	--confirm-all-prompts)
		CONFIRMALL=1
		shift 1
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
	--agentguid)
		AGENTGUID="$2"
		shift 2
		;;
	--cloud)
		CLOUD="$2"
		shift 2
		;;
	--preview)
		PREVIEW=1
		shift 1
		;;
	--multi-clients)
		MULTICLIENTS=1
		shift 1
		;;
	--script-debug)
		set -x
		shift 1
		;;
	-*)
		echo "Unknown option $1"
		echo "Valid options are"
		echo "--keymode [kvmi|kvsi|cfgf]"
		echo "--connectionmode [abap|mserv]"
		echo "--configpath <path>"
		echo "--abapserver <servername>"
		echo "--systemnr <system number>"
		echo "--sid <SID>"
		echo "--clientnumber <client number>"
		echo "--messageserverhost <servername>"
		echo "--messageserverport <servername>"
		echo "--logongroup <logon group>"
		echo "--sapusername <username>"
		echo "--sappassword <password>"
		echo "--sdk <filename>"
		echo "--appid <guid>"
		echo "--appsecret <secret>"
		echo "--tenantid <guid>"
		echo "--kvaultname <keyvaultname>"
		echo "--loganalyticswsid <id>"
		echo "--loganalyticskey <key>"
		echo "--use-snc"
		echo "--cryptolib <sapcryptolibfilename>"
		echo "--sapgenpse <sapgenpsefilename>"
		echo "--client-cert <client certificate filename>"
		echo "--client-key <client key filename>"
		echo "--cacert <trusted ca cert> --cacert <trusted ca cert>..."
		echo "--client-pfx <pfx filename>"
		echo "--client-pfx-passwd <password>"
		echo "--server-cert <server certificate filename>"
		echo "--http-proxy <proxy url>"
		echo "--confirm-all-prompts"
		echo "--preview"
		echo "--multi-clients"
		exit 1
		;;
	*)
		POSITIONAL_ARGS+=("$1") # save positional arg
		shift                   # past argument
		;;
	esac
done

if [ -n "$SDKFILELOC" ] && [ ! -f "$SDKFILELOC" ]; then
	echo 'Invalid SDK path'
	exit 1
fi

# End of parameter validation

#Globals
containername=sapcon
sysconf=systemconfig.ini

os=$(awk </etc/os-release 'BEGIN { FS="=" } $1=="ID" {print $2}')
ver_id=$(awk </etc/os-release 'BEGIN { FS="=" } $1=="VERSION_ID" {print $2}' | awk '{print substr($0, 2, length($0) - 2) }')
id_like=$(awk </etc/os-release 'BEGIN { FS="=" } $1=="ID_LIKE" {print $2}')
echo "Running on $os version $ver_id id $id_like"

#Installing prerequisites
if [ "$os" == "ubuntu" ]; then
	#Ubuntu
	echo 'Updating package lists'
	sudo apt-get update >/dev/null
	install_package "jq" "apt install -y -qq"
	install_package "unzip" "apt install -y -qq"
	install_package "docker.io" "apt install -y -qq"
	echo "Installing docker"
	if [ "$MODE" != "cfgf" ]; then
		echo "Installing Azure CLI"
		curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash >/dev/null 2>&1
	fi

elif [ "$os" == '"rhel"' ]; then
	#RHEL
	echo 'Updating package lists'
	sudo yum update -y --disablerepo='*' --enablerepo='*microsoft*' >/dev/null
	install_package "nc" "yum install -y"
	install_package "jq" "yum install -y"

	if [ "$MODE" != "cfgf" ]; then
		sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc >/dev/null
		echo -e "[azure-cli]\nname=Azure CLI\nbaseurl=https://packages.microsoft.com/yumrepos/azure-cli\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" | sudo tee /etc/yum.repos.d/azure-cli.repo >/dev/null
		echo "Installing Azure CLI"
		sudo yum install azure-cli -y >/dev/null
	fi
	sudo yum install -y yum-utils >/dev/null
	sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo >/dev/null
	echo "Installing Docker"
	sudo yum install docker-ce docker-ce-cli containerd.io -y >/dev/null
	sudo systemctl enable docker.service
	sudo systemctl start docker.service

elif [ "$os" == '"sles"' ]; then
	# SUSE
	echo "Updating package lists"
	sudo zypper refresh >/dev/null
	echo "Updating installed packages"
	sudo zypper update -y >/dev/null
	install_package "curl" "zypper install -y"
	install_package "jq" "zypper install -y"
	install_package "docker" "zypper install -y"
	sudo systemctl enable docker.service
	sudo systemctl start docker.service

	if [ "$MODE" != "cfgf" ]; then
		if ! rpm -qa | grep gpg-pubkey-be1229cf-5631588c >/dev/null; then
			sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc >/dev/null
			echo "Adding Microsoft GPG key"
		fi
		if ! sudo zypper lr | grep "Azure CLI" >/dev/null; then
			sudo zypper addrepo --name 'Azure CLI' --check https://packages.microsoft.com/yumrepos/azure-cli azure-cli >/dev/null
			echo "Adding Microsoft Azure CLI repository"
		fi
		if which az >/dev/null 2>&1; then
			#AZ is installed, check if it is out-of date version with compatibility issues
			azver=$(az version | jq '."azure-cli"')
			if verlte "2.33.1" "$azver"; then
				echo "Installed version $azver is out of date, removing older version"
				sudo zypper rm -y --clean-deps azure-cli >/dev/null
				echo "Installing Azure CLI"
				sudo zypper install -y --from azure-cli azure-cli >/dev/null
			fi
		else
			echo "Installing Azure CLI"
			sudo zypper install -y --from azure-cli azure-cli >/dev/null
		fi
	fi
else
	echo OS version is not suppored. Supported OS: Ubuntu version 18.04 or higher, SLES version 15 or higher, or RHEL version 7.7 or higher
	exit 1
fi

dockerimage=mcr.microsoft.com/azure-sentinel/solutions/sapcon
if [ $CLOUD == 'public' ]; then
	tagver=':latest'
elif [ $CLOUD == 'fairfax' ]; then
	tagver=':ffx-latest'
	az cloud set --name "AzureUSGovernment" >/dev/null 2>&1
elif [ $CLOUD == 'mooncake' ]; then
	tagver=':mc-latest'
	az cloud set --name "AzureChinaCloud" >/dev/null 2>&1
fi

if [ $PREVIEW ]; then
	tagver="$tagver-preview"
fi

# sudo groupadd docker
echo "Creating group 'docker' and adding current user to 'docker' group"
sudo usermod -aG docker "$USER"

if [ "$MODE" == "kvmi" ]; then
	echo "Validating Azure managed identity"
	az login --identity --allow-no-subscriptions >/dev/null 2>&1
	if [ ! $? -eq 0 ]; then
		printf 'VM is not set with managed identity or the AZ client was not installed correctly.\nSet and grant relevant Key Vault permissions and make sure that Azure CLI is installed by running "az login"\nFor more information check - https://docs.microsoft.com/cli/azure/install-azure-cli'
		exit 1
	fi
elif [ "$MODE" == "kvsi" ]; then
	echo "Validating service principal identity"
	az login --service-principal -u "$APPID" -p "$APPSECRET" --tenant "$TENANT" --allow-no-subscriptions >/dev/null 2>&1
	if [ ! $? -eq 0 ]; then
		echo "Logon with $APPID failed, please check application ID, secret and tenant ID. Ensure the application has been added as an enterprise application"
		exit 1
	fi
	az keyvault secret list --id "https://$kv.vault.azure.net/" >/dev/null 2>&1
	if [ ! $? -eq 0 ]; then
		echo "Cannot connect to keyvault $kv. Make sure application $APPID has been granted privileges to the keyvault"
		exit 1
	fi
fi

echo 'Deploying Azure Sentinel SAP data connector.'

echo 'Starting Docker image pull'

sudo docker pull $dockerimage$tagver
if [ $? -eq 1 ]; then
	echo 'Error downloading the Azure Sentinel SAP data connector.'
	exit 1
fi
echo 'Latest Azure Sentinel data connector downloaded successfully.'

for container in "${containers[@]}"; do
	read -r var1 var2 var3 <<< "$container"
	SID=$var1
	if [[ -n $var3 ]]; then
		CLIENTNUMBER=$var2
		AGENTGUID=$var3
		MULTICLIENTS=true
	else
		AGENTGUID=$var2
		MULTICLIENTS=false
		CLIENTNUMBER=""
	fi
	echo "creating AGENTGUID: $AGENTGUID, SID: $SID, CLIENTNUMBER: $CLIENTNUMBER"	

	if [ -z "$SID" ]; then
		read -r -p 'SID : ' SID
		while [ ${#SID} -ne 3 ]; do
			echo 'Invalid SID, SID length should be 3'
			read -r -p 'SID: ' SID
		done
	fi

	if [ $MULTICLIENTS ]; then
		intprefix="$SID-$CLIENTNUMBER"
	else
		intprefix="$SID"
	fi

	sysfileloc=$CONFIGPATH/$containername/$intprefix/
	sudo chown "$USER" "$sysfileloc"
	if [ ! $? -eq 0 ]; then
		echo 'Error creating the local folder.'
		exit 1
	fi

	# Try to locate the SDK file in current folder
	if [ -z "$SDKFILELOC" ]; then
		SDKFILELOC=$(ls -1 nwrfc*.zip | head -1)
		#try to locate the SDK file in home dir
		if [ -z "$SDKFILELOC" ]; then
			SDKFILELOC=$(sudo find "$(pwd)" -name "nwrfc*.zip" -type f | head -1)
		fi
	fi

	while [ -z "$SDKFILELOC" ] || [ ! -f "$SDKFILELOC" ]; do
		echo 'Enter the full file location path of your downloaded SAP NetWeaver SDK zip. To download the SDK use the following link:\n https://launchpad.support.sap.com/#/softwarecenter/template/products/%20_APP=00200682500000001943&_EVENT=DISPHIER&HEADER=Y&FUNCTIONBAR=N&EVENT=TREE&NE=NAVIGATE&ENR=01200314690100002214&V=MAINT&TA=ACTUAL&PAGE=SEARCH/SAP%20NW%20RFC%20SDK \nSelect SAP NW RFC SDK 7.50 -> Linux on X86_64 64BIT -> Download the latest version\nExample: /home/user/nwrfc750P_x-70002752.zip'
		SDKFILELOC=""
		read_value SDKFILELOC 'SDK file location'
		SDKFILELOC="${SDKFILELOC/#\~/$HOME}"
	done

	#Building the container
	containername="$containername-$intprefix"

	sudo docker inspect "$containername" >/dev/null 2>&1
	if [ $? -eq 0 ]; then
		echo "Azure Sentinel SAP connector is already installed for instance $intprefix. The previous connector will be removed and replaced by the new version."
		pause 'Press any key to update'
		sudo docker stop "$containername" >/dev/null
		sudo docker container rm "$containername" >/dev/null
	fi
	sncline=""

	if [ -n "$HTTPPROXY" ]; then
		httpproxyline="-e HTTP_PROXY=$HTTPPROXY"
	fi
	cmdparams=" --label Cloud=$CLOUD"
	# Generating SENTINEL_AGENT_GUID
	cmdparams+=" -e SENTINEL_AGENT_GUID=$AGENTGUID "

	if [ "$MODE" == "kvmi" ]; then
		echo "Creating docker container for use with Azure Key vault and managed VM identity"
		sudo docker create -v "$sysfileloc":/sapcon-app/sapcon/config/system $cmdparams $sncline $httpproxyline --name "$containername" $dockerimage$tagver >/dev/null
	elif [ "$MODE" == "kvsi" ]; then
		echo "Creating docker container for use with Azure Key vault and application authentication"
		sudo docker create -v "$sysfileloc":/sapcon-app/sapcon/config/system $cmdparams $sncline $httpproxyline -e AZURE_CLIENT_ID="$APPID" -e AZURE_CLIENT_SECRET="$APPSECRET" -e AZURE_TENANT_ID="$TENANT" --name "$containername" $dockerimage$tagver >/dev/null
	elif [ "$MODE" == "cfgf" ]; then
		echo "Creating docker container for use with secrets in config file"
		sudo docker create -v "$sysfileloc":/sapcon-app/sapcon/config/system $cmdparams $sncline $httpproxyline --name "$containername" $dockerimage$tagver >/dev/null
	fi
	echo 'Azure Sentinel SAP connector was updated for instance '"$intprefix"

	sudo docker cp "$SDKFILELOC" "$containername":/sapcon-app/inst/ >/dev/null
	if [ $? -eq 0 ]; then
		echo 'SDK archive was successfully updated'
	else
		echo 'Azure Sentinel data connector upgrade failed. The NetWeaver SDK could not be added to the image'
		exit 1
	fi
done

# Docker Configurations
newgrp docker
