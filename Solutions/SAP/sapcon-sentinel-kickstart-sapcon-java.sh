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
# java
# sapcontrol

MODE="kvmi"
CONNECTIONMODE=""
CONFIGPATH="/opt"
TRUSTEDCA=()
CLOUD='public'
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
	--connectionmode)
		CONNECTIONMODE="$2"
		shift 2
		;;
	--abapospass)
		ABAPOSPASS="$2"
		shift 2
		;;
	--abaposuser)
		ABAPOSUSER="$2"
		shift 2
		;;
	--javaospass)
		JAVAOSPASS="$2"
		shift 2
		;;
	--javaosuser)
		JAVAOSUSER="$2"
		shift 2
		;;
	--abapspserver)
		ABAPSPSERVER="$2"
		shift 2
		;;
	--abapsptz)
		ABAPSPTZ="$2"
		shift 2
		;;
	--abapspinstance)
		ABAPSPINSTANCE="$2"
		shift 2
		;;
	--javaappserver)
		JAVAAPPSERVER="$2"
		shift 2
		;;
	--javainstance)
		JAVAINSTANCE="$2"
		shift 2
		;;
	--javatz)
		JAVATZ="$2"
		shift 2
		;;
	--sid)
		SID="$2"
		shift 2
		;;
    --hostnetwork)
		HOSTNETWORK=1
		shift 1
		;;
    --azureresourceid)
		AZURERESOURCEID="$2"
		shift 
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
	--http-proxy)
		HTTPPROXY="$2"
		shift 2
		;;
--local-img)
		LOCALIMG="$2"
		shift 2
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
		echo "--connectionmode [abap|mserv]"
		echo "--abapserver <servername>"
		echo "--systemnr <system number>"
		echo "--sid <SID>"
		echo "--clientnumber <client number>"
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
		echo "--preview"
		exit 1
		;;
	*)
		POSITIONAL_ARGS+=("$1") # save positional arg
		shift                   # past argument
		;;
	esac
done
# Parameter set validation
if [ "$MODE" != 'kvsi' ] && [ "$MODE" != 'kvmi' ] && [ "$MODE" != 'cfgf' ]; then
	echo 'Invalid setting for --keymode. Supported values are "kvsi", "kvmi" or "cfgf"'
	exit 1
fi

if [ "$CONNECTIONMODE" != 'java' ] && [ "$CONNECTIONMODE" != 'sapcontrol' ]; then
	echo 'Invalid setting for --connectionmode. Supported values are "java", "sapcontrol"'
	exit 1
fi

if [ "$CONNECTIONMODE" == "java" ]; then
	if [ -z "$JAVAAPPSERVER" ] || [ -z "$JAVAINSTANCE" ] || [ -z "$JAVATZ" ] || [ -z "$JAVAOSUSER" ] || [ -z "$JAVAOSPASS" ]; then
		echo "Error: Missing required variables for Java connection mode"
        echo "Required variables: JAVAAPPSERVER, JAVAINSTANCE, JAVATZ, JAVAOSUSER, JAVAOSPASS"
		exit 1
	fi
fi

if [ "$CONNECTIONMODE" == "sapcontrol" ]; then
	if [ -z "$ABAPSPSERVER" ] || [ -z "$ABAPSPTZ" ] || [ -z "$ABAPSPINSTANCE" ] || [ -z "$ABAPOSPASS" ] || [ -z "$ABAPOSUSER" ]; then
		echo "Error: Missing required variables for SAPControl connection mode"
		echo "Required variables: ABAPSPSERVER, ABAPSPTZ, ABAPSPINSTANCE, ABAPOSPASS, ABAPOSUSER"
		exit 1
	fi
fi


if [ "$MODE" == 'kvsi' ] && { [ -z "$APPID" ] || [ -z "$APPSECRET" ] || [ -z "$TENANT" ] || [ -z "$kv" ]; }; then
	printf 'Missing parameter values. -m kvsi requires --appid, --appsecret, --tenantid, --kvaultname parameters.\nProvide values interactively now or rerun the script with relevant switches.'
	read_value APPID "Application ID"
	read_value APPSECRET "Application Secret"
	read_value TENANT "Tenant ID"
	read_value kv "Keyvault Name"
fi

if [ -n "$SDKFILELOC" ] && [ ! -f "$SDKFILELOC" ]; then
	echo 'Invalid SDK path'
	exit 1
fi

if [ "$CLOUD" != 'public' ] && [  "$CLOUD" != 'fairfax' ] && [  "$CLOUD" != 'mooncake' ]; then
	echo 'Invalid cloud name, avilable options: public, fairfax, mooncake.'
	exit 1
fi

# End of parameter validation
echo '
************************************************************
THIS INSTALLATION SCRIPT WILL USE ROOT ACCESS TO:

1. DOWNLOAD, INSTALL AND CONFIGURE DOCKER IMAGE
2. ADD THE CURRENT USER TO THE DOCKER GROUP
3. RUN THE CONNECTOR AS A DOCKER CONTAINER ON THE HOST

*************************************************************
The Azure Sentinel SAP solution is currently in PREVIEW. 

The Azure Preview Supplemental Terms include additional legal terms that apply to Azure features that are in beta, preview, or otherwise not yet released into general availability.

For more information, see https://azure.microsoft.com/support/legal/preview-supplemental-terms/.
****

-----Microsoft continuous threat monitoring for SAP KickStart script----

In order to complete the installation process, you need:

- SAP version: The Azure Sentinel SAP Logs connector requires a SAP version of 7.4 or higher.

- SAP system details: Make a note of your SAP system IP address, system number, system ID, and client for use during the installation.

- SAP change requests: Import any required change requests for your logs from the CR folder of this repository - https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/SAP/CR.

Configure the following SAP Log change requests to enable support for ingesting specific SAP logs into Azure Sentinel.
- SAP Basis versions 7.5 and higher:  install NPLK900180
- SAP Basis version 7.4:  install NPLK900179
- To create your SAP role in any SAP version: install NPLK900163

Tip: To create your SAP role with all required authorizations, deploy the SAP change request NPLK900140 on your SAP system. 
This change request creates the /msftsen/sentinel_connector role, and assigns the role to the ABAP connecting to Azure Sentinel.

Note: The required SAP log change requests expose custom RFC FMs that are required for the connector, and do not change any standard or custom objects.

For more information see the SAP documentation.
'

pause '[Press enter to agree and proceed as we guide you through the installation process. Alternately, press CTRL+C to cancel the process]'

#Globals
containername=sapcon
sysconf=systemconfig.json
settingsjson=settings.json

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

if [ $DEVMODE ]; then
	dockerimage=$(echo "$DEVURL" | awk -F: '{print $1}')
	acr=$(echo "$DEVURL" | awk -F/ '{print $1}')
	sudo docker login "$acr" -u "$DEVACRLOGIN" -p "$DEVACRPWD"
	tagver=$(echo "$DEVURL" | awk -F: '{print ":"$2}')
# elif [ -n $LOCALIMG ]; then
# 	dockerimage="$LOCALIMG"
# 	tagver=''
else
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

fi


# sudo groupadd docker
echo "Creating group 'docker' and adding current user to 'docker' group"
sudo usermod -aG docker "$USER"

if { [ "$MODE" == 'kvmi' ] && [ -z "$kv" ]; } || { [ "$MODE" == 'kvsi' ] && [ -z "$kv" ]; }; then
	read_value kv "KeyVault Name"
fi

validateKeyVault() {
	az keyvault secret list --id "https://$kv.vault.azure.net/" >/dev/null 2>&1
	if [ ! $? -eq 0 ]; then
		echo "Cannot connect to Key Vault $kv. Agent identity must have 'Key Vault Secrets User' role or list, get secret permissions."
		exit 1
	fi
}

if [ "$MODE" == "kvmi" ]; then
	echo "Validating Azure managed identity"
	az login --identity --allow-no-subscriptions >/dev/null 2>&1
	if [ ! $? -eq 0 ]; then
		printf 'VM is not set with managed identity or the AZ client was not installed correctly.\nSet and grant relevant Key Vault permissions and make sure that Azure CLI is installed by running "az login"\nFor more information check - https://docs.microsoft.com/cli/azure/install-azure-cli'
		exit 1
	fi
	validateKeyVault
elif [ "$MODE" == "kvsi" ]; then
	echo "Validating service principal identity"
	az login --service-principal -u "$APPID" -p "$APPSECRET" --tenant "$TENANT" --allow-no-subscriptions >/dev/null 2>&1
	if [ ! $? -eq 0 ]; then
		echo "Logon with $APPID failed, please check application ID, secret and tenant ID. Ensure the application has been added as an enterprise application"
		exit 1
	fi
	validateKeyVault
fi

echo 'Deploying Azure Sentinel SAP data connector.'

echo 'Starting Docker image pull'
# pull only if LOCALIMG is not set
if [ -z $LOCALIMG ]; then
	sudo docker pull $dockerimage$tagver
	if [ $? -eq 1 ]; then
		echo 'Error downloading the Azure Sentinel SAP data connector.'
		exit 1
	fi
	echo 'Latest Azure Sentinel data connector downloaded successfully.'
fi

if [ -z "$SID" ]; then
	read -r -p 'SID : ' SID
	while [ ${#SID} -ne 3 ]; do
		echo 'Invalid SID, SID length should be 3'
		read -r -p 'SID: ' SID
	done
fi

intprefix="$SID"

sysfileloc=$CONFIGPATH/$containername/$intprefix/
sudo mkdir -p "$sysfileloc"
sudo chown "$USER" "$sysfileloc"
if [ ! $? -eq 0 ]; then
	echo 'Error creating the local folder.'
	exit 1
fi

if [ -z "$logwsid" ]; then
	read -r -p 'Log Analytics Workspace ID : ' logwsid
	while [ -z "$logwsid" ]; do
		echo 'Log Analytics workspace ID is empty - try again'
		read -r -p 'Log Analytics Workspace ID : ' logwsid
	done
fi

read_password logpubkey 'Log Analytics Public Key'
while [ -z "$logpubkey" ]; do
	echo 'Log Analytics Public Key empty- try again'
	read_password logpubkey 'Log Analytics Public Key'
done

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

#Verifying SDK version only in case of non-fedora OS
if [ "$os" != "fedora" ]; then
	unzip -o "$SDKFILELOC" -d /tmp/ > /dev/null 2>&1
	SDKLOADRESULT=$(ldd /tmp/nwrfcsdk/lib/libsapnwrfc.so 2>&1)
	sdkok=$?
	rm -rf /tmp/nwrfcsdk
	if [ ! $sdkok -eq 0 ]; then
		echo "Invalid SDK supplied. The error while attempting to load the SAP NetWeaver SDK:"
		echo $SDKLOADRESULT
		echo "Please rerun script supplying version of SAP NetWeaver SDK compatible with the current OS platform"
		exit 1
	fi
fi

intprefix="$SID"

#Building the container
containername="$containername-$intprefix"

sudo docker inspect "$containername" >/dev/null 2>&1
if [ $? -eq 0 ]; then
	echo "Azure Sentinel SAP connector is already installed for instance $intprefix. The previous connector will be removed and replaced by the new version."
	pause 'Press any key to update'
	sudo docker stop "$containername" >/dev/null
	sudo docker container rm "$containername" >/dev/null
fi

if [ -n "$HTTPPROXY" ]; then
	httpproxyline="-e HTTP_PROXY=$HTTPPROXY"
fi
cmdparams=" --label Cloud=$CLOUD"
# Generating SENTINEL_AGENT_GUID
cmdparams+=" -e SENTINEL_AGENT_GUID=$(uuidgen) "

if [ $HOSTNETWORK ]; then
	cmdparams+=" --network host"
fi

if [ "$MODE" == "kvmi" ]; then
	echo "Creating docker container for use with Azure Key vault and managed VM identity"
	sudo docker create -v "$sysfileloc":/sapcon-app/sapcon/config/system $cmdparams $httpproxyline --name "$containername" $dockerimage$tagver >/dev/null
elif [ "$MODE" == "kvsi" ]; then
	echo "Creating docker container for use with Azure Key vault and application authentication"
	sudo docker create -v "$sysfileloc":/sapcon-app/sapcon/config/system $cmdparams $httpproxyline -e AZURE_CLIENT_ID="$APPID" -e AZURE_CLIENT_SECRET="$APPSECRET" -e AZURE_TENANT_ID="$TENANT" --name "$containername" $dockerimage$tagver >/dev/null
elif [ "$MODE" == "cfgf" ]; then
	echo "Creating docker container for use with secrets in config file"
	sudo docker create -v "$sysfileloc":/sapcon-app/sapcon/config/system $cmdparams $httpproxyline --name "$containername" $dockerimage$tagver >/dev/null
fi
echo 'Azure Sentinel SAP connector was updated for instance '"$intprefix"

sudo docker cp "$containername":/sapcon-app/template/systemconfig-kickstart-blank.json "$sysfileloc$sysconf"
if [ ! $? -eq 0 ]; then
	echo 'Error accessing the local folder.'
	exit 1
fi

### start of json config creation

# Generate a GUID for the root key
GUID=$(uuidgen)

# jq --arg guid "$GUID" '{ ($guid): . }' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"

# Attempt to run the jq commands
jq '.abap_table_selector = {}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
jq '.logs_activation_status = {}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
jq 'del(.abap_central_instance)' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"

if [ "$CONNECTIONMODE" == 'java' ]; then
    jq --arg j2etz "$JAVATZ" '.file_extraction_java += {"javatz": $j2etz}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
    jq --arg j2einstance "$JAVAINSTANCE" '.file_extraction_java += {"javainstance": $j2einstance}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
    jq --arg j2eappserver "$JAVAAPPSERVER" '.file_extraction_java += {"javaappserver": $j2eappserver}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
	jq '.logs_activation_status += {"javafileslogs": "True"}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
	jq '.logs_activation_status.javafileslogs = "True"' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
elif [ "$CONNECTIONMODE" == 'sapcontrol' ]; then
    jq --arg abapinstance "$ABAPSPINSTANCE" '.file_extraction_abap += {"instance": $abapinstance}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
    jq --arg abaptz "$ABAPSPTZ" '.file_extraction_abap += {"abaptz": $abaptz}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
    jq --arg appserver "$ABAPSPSERVER" '.file_extraction_abap += {"appserver": $appserver}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
	jq '.logs_activation_status += {"abapfileslogs": "True"}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
	jq '.logs_activation_status.abapfileslogs = "True"' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
fi

if [ -n "$AZURERESOURCEID" ]; then
    jq --arg azure_resource_id "$AZURERESOURCEID" '.Azure Credentials += {"azure_resource_id": $azure_resource_id}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
fi

if [ "$MODE" == 'kvmi' ] || [ "$MODE" == 'kvsi' ]; then
    jq '.secrets_source += {"secrets": "AZURE_KEY_VAULT"}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
    jq --arg intprefix "$intprefix" '.secrets_source += {"intprefix": $intprefix}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
    jq --arg keyvault "$kv" '.secrets_source += {"keyvault": $keyvault}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
	
	
	echo 'Setting secrets in Azure Key Vault'
	echo 'Please sign-in with a user that has access to set secrets in Azure Key Vault.'
	az login
	if [ ! $? -eq 0 ]; then
		echo 'Unable to sign-in to Azure. Exiting.'
		exit 1
	fi

	if [ "$CONNECTIONMODE" == 'java' ]; then
		az keyvault secret set --name "$intprefix"-JAVAOSUSER --value "$JAVAOSUSER" --description SECRET_JAVA_OS_USER --vault-name "$kv" >/dev/null
		az keyvault secret set --name "$intprefix"-JAVAOSPASS --value "$JAVAOSPASS" --description SECRET_JAVA_OS_PASS --vault-name "$kv" >/dev/null
	elif [ "$CONNECTIONMODE" == 'sapcontrol' ]; then
		az keyvault secret set --name "$intprefix"-ABAPOSUSER --value "$ABAPOSUSER" --description SECRET_ABAP_OS_USER --vault-name "$kv" >/dev/null
		az keyvault secret set --name "$intprefix"-ABAPOSPASS --value "$ABAPOSPASS" --description SECRET_ABAP_OS_PASS --vault-name "$kv" >/dev/null
	fi

	az keyvault secret set --name "$intprefix"-LOGWSID --value "$logwsid" --description SECRET_LOGWSID --vault-name "$kv" >/dev/null
	if [ ! $? -eq 0 ]; then
		echo 'Unable to set secrets in Azure Key Vault'
		echo 'Make sure user identity has permission to set secrets in the Key Vault.'
		exit 1
	fi
	az keyvault secret set --name "$intprefix"-LOGWSPUBLICKEY --value "$logpubkey" --description SECRET_LOGWSPUBKEY --vault-name "$kv" >/dev/null

elif [ "$MODE" == 'cfgf' ]; then
    jq '.secrets_source += {"secrets": "DOCKER_FIXED"}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
    jq --arg logwsidjs "$logwsid" '.azure_credentials += {"loganalyticswsid": $logwsidjs}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
    jq --arg logpubkeyjs "$logpubkey" '.azure_credentials += {"publickey": $logpubkeyjs}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
	
	if [ "$CONNECTIONMODE" == 'java' ]; then
		jq --arg j2eosuser "$JAVAOSUSER" '.file_extraction_java += {"javaosuser": $j2eosuser}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
		jq --arg j2eospasswd "$JAVAOSPASS" '.file_extraction_java += {"javaospasswd": $j2eospasswd}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
	elif [ "$CONNECTIONMODE" == 'sapcontrol' ]; then
		jq --arg osuser "$ABAPOSUSER" '.file_extraction_abap += {"osuser": $osuser}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
		jq --arg ospasswd "$ABAPOSPASS" '.file_extraction_abap += {"ospasswd": $ospasswd}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"
	fi
fi


jq -s --arg GUID "$GUID" '.[0] | {($GUID): .}' "$sysfileloc$sysconf" > "$sysfileloc$sysconf.tmp" && mv "$sysfileloc$sysconf.tmp" "$sysfileloc$sysconf"

### end of json config creation

# #populate settings.json
echo $UPDATEPOLICY> "$sysfileloc$settingsjson"

echo 'System information and credentials Has been Updated'

sudo docker cp "$SDKFILELOC" "$containername":/sapcon-app/inst/ >/dev/null
if [ $? -eq 0 ]; then
	echo 'SDK archive was successfully updated'
else
	echo 'Azure Sentinel data connector upgrade failed. The NetWeaver SDK could not be added to the image'
	exit 1
fi

sudo docker start "$containername" >/dev/null
if [ $? -eq 0 ]; then
	echo '
Azure Sentinel SAP connector was started - quick reference for future steps:
View logs: docker logs '"$containername"'
View logs continuously: docker logs -f '"$containername"'
Stop the connector: docker stop '"$containername"'
Start the connector: docker start '"$containername"'
The process has been successfully completed, thank you!'
else
	echo 'Azure Sentinel Connector upgrade failed - the NetWeaver SDK could not be added to the image'
	exit 1
fi
# Docker Configurations
newgrp docker
