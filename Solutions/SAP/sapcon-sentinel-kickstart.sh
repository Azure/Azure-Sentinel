#!/bin/bash

# if [ "$EUID" -ne 0 ]
#   then echo "Please run as root"
#   exit
# fi

echo '

************************************************************

THIS INSTALLATION SCRIPT WILL USE ROOT ACCESS TO:

1. INSTALL AND EXTRACT DOCKER IMAGE

2. ADD THE CURRENT USER TO THE DOCKER GROUP

3. RUN THE CONNECTOR AS A DOCKER CONTAINER ON THE HOST

*************************************************************
The Azure Sentinel SAP solution is currently in PREVIEW. 

The Azure Preview Supplemental Terms include additional legal terms that apply to Azure features that are in beta, preview, or otherwise not yet released into general availability.

For more information, see https://azure.microsoft.com/support/legal/preview-supplemental-terms/.
****'

function pause(){
   read -p "$*"
}

echo '
-----Sapcon on Azure – ABAP only KickStart----

In order to complete the installation process, you need:

- Your SAP Continuous Threat Monitoring container registry password. 
The access and password must be granted explicitly to you by Microsoft, is personal and may not be shared. 

- SAP version: The Azure Sentinel SAP Logs connector requires a SAP version of 7.4 or higher.

- SAP system details: Make a note of your SAP system IP address, system number, system ID, and client for use during the installation.

- SAP change requests: Import any required change requests for your logs from the CR folder of this repository - https://github.com/Azure/AzureSentinel4SAP/tree/main/CR.

Configure the following SAP Log change requests to enable support for ingesting specific SAP logs into Azure Sentinel.
- SAP Basis versions 7.5 and higher:  install NPLK900131
- SAP Basis version 7.4:  install NPLK900132
- To create your SAP role in any SAP version: install NPLK900114

Tip: To create your SAP role with all required authorizations, deploy the SAP change request NPLK900114 on your SAP system. 
This change request creates the /msftsen/sentinel_connector role, and assigns the role to the ABAP connecting to Azure Sentinel.

SAP notes required for versions earlier than SAP Basis 7.5 SP13:
- SAP Note 2641084, named *Standardized read access for the Security Audit log data*
- SAP Note 2173545, named *CHANGEDOCUMENT_READ_ALL*
- SAP Note 2502336, named *RSSCD100 - read only from archive, not from database*

Note: The required SAP log change requests expose custom RFC FMs that are required for the connector, and do not change any standard or custom objects.

For more information see the SAP documentation.
'

pause '[Press enter to agree and proceed as we guide you through the installation process. Alternately, press CTRL+C to cancel the process]'


#Globals
dockerimage=mcr.microsoft.com/azure-sentinel/solutions/sapcon
containername=sapcon
sysconf=systemconfig.ini
tagver=":latest-preview"
logwsid=LOGWSID
logwspubkey=LOGWSPUBLICKEY
abapuser=ABAPUSER
abappass=ABAPPASS

os=$(cat /etc/os-release | awk 'BEGIN { FS="=" } $1=="ID" {print $2}')
ver_id=$(cat /etc/os-release | awk 'BEGIN { FS="=" } $1=="VERSION_ID" {print $2}' | awk '{print substr($0, 2, length($0) - 2) }')
id_like=$(cat /etc/os-release | awk 'BEGIN { FS="=" } $1=="ID_LIKE" {print $2}')

echo 'Starting OS update. This process may take a few minutes.'

if [ $os == "ubuntu" ]
then
	#Ubuntu
	sudo apt-get update >/dev/null
	sudo apt-get install -y -qq jq docker.io unzip >/dev/null
	curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash >/dev/null 2>&1

elif [ $os == '"rhel"' ]
then
	#RHEL
	sudo yum update -y --disablerepo='*' --enablerepo='*microsoft*' >/dev/null
	sudo yum install -y nc >/dev/null
	sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc >/dev/null
	echo -e "[azure-cli]
name=Azure CLI
baseurl=https://packages.microsoft.com/yumrepos/azure-cli
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc" | sudo tee /etc/yum.repos.d/azure-cli.repo >/dev/null
	sudo yum install azure-cli -y >/dev/null
	sudo yum install -y yum-utils >/dev/null
	sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo >/dev/null
	sudo yum install docker-ce docker-ce-cli containerd.io -y >/dev/null
	sudo systemctl enable docker.service
	sudo systemctl start docker.service

elif [ $os == '"sles"' ]
then
	# SUSE
	sudo zypper update -y >/dev/null
	sudo zypper install -y curl >/dev/null
	sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc >/dev/null
	sudo zypper addrepo --name 'Azure CLI' --check https://packages.microsoft.com/yumrepos/azure-cli azure-cli >/dev/null
	sudo zypper install -y --from azure-cli azure-cli >/dev/null
	sudo zypper install -y docker >/dev/null
	sudo systemctl enable docker.service 
	sudo systemctl start docker.service 

else
	echo VM version is not sufficient. Create one of the following VM OS images: Ubuntu version 18.04 or higher, SLES version 15 or higher, or RHEL version 7.7 or higher
	exit 1
fi


# sudo groupadd docker
sudo usermod -aG docker $USER
az login --identity --allow-no-subscriptions >/dev/null 2>&1
if [ ! $? -eq 0 ]
then 
	echo 'VM is not set with managed identity or the AZ client was not installed correctly.
Set and grant relevant Key Vault permissions and make sure that Azure CLI is installed by running "az login", for more information check - https://docs.microsoft.com/cli/azure/install-azure-cli .'
	exit 1
fi  

echo '
VM is ready to deploy the Azure Sentinel SAP data connector. All OS dependencies are met. 
'

echo 'Starting Docker image pull'
sudo docker pull $dockerimage$tagver
if [ $? -eq 1 ];
then 
	echo 'Error downloading the Azure Sentinel SAP data connector.'
	exit 1
fi
pause 'Latest Azure Sentinel data connector downloaded successfully. Press ENTER to continue.
'
echo 'Enter the following information about your SAP instance:
'
read -p 'Hostname: ' hostvar
read -p 'System Number: ' sysnrvar
read -p 'SID : ' sysid
while [ ${#sysid} -ne 3 ] 
do
	echo 'Invalid SID - try again'
	read -p 'SID: ' sysid
done 

read -p 'Client: ' clientvar
while [ ${#clientvar} -ne 3 ]
do
	echo 'Invalid Client - try again'
	read -p 'Client: ' clientvar
done 

echo '
Testing network access to SAP instance'
timeout 2 nc -z $hostvar 33$sysnrvar >/dev/null
portcheck1=$?

if [ ! $portcheck1 -eq 0 ]
then
	echo "Port 33$sysnrvar is not accessible. Allow access and run this script again."
	exit 1
fi

timeout 2 nc -z $hostvar 32$sysnrvar
portcheck2=$?
if [ ! $portcheck2 -eq 0 ]
then
	echo "Port 32$sysnrvar is not accessible. Allow access and run this script again."
	exit 1
fi
echo 'SAP system is reachable
'

sysfileloc=$(pwd)/$containername/$sysid/
mkdir -p $sysfileloc
if [ ! $? -eq 0 ];
then 
	echo 'Error creating the local folder.'
	exit 1
fi

containername="$containername-$sysid"

sudo docker create -v $sysfileloc:/sapcon-app/sapcon/config/system --name $containername $dockerimage$tagver >/dev/null
if [ $? -eq 1 ];
then 
	echo '
Azure Sentinel SAP connector is already installed. The previous connector will be removed and replaced by the new version.'
	pause 'Press any key to update'
	sudo docker stop $containername >/dev/null
	sudo docker container rm $containername >/dev/null
	sudo docker create -v $sysfileloc:/sapcon-app/sapcon/config/system --name $containername $dockerimage >/dev/null
	echo 'Azure Sentinel SAP connector was updated for instance '"$sysid"
	pause 'Press any key to continue'
fi


sudo docker cp $containername:/sapcon-app/template/systemconfig-kickstart.ini "$sysfileloc"systemconfig.ini
if [ ! $? -eq 0 ];
then 
	echo 'Error accessing the local folder.'
	exit 1
fi

echo 'Enter the key vault name followed by your SAP and Azure Sentinel credentials. 
Make sure that this VM has managed identity set with the relevant authentication for your Key Vault.'

read -p 'KeyVault Name: ' kv
while [ -z $kv ]
do
	echo 'KeyVault is empty - try again'
	read -p 'KeyVault: ' kv
done 

read -rp 'SAP Username: ' uservar
while [ -z "$uservar" ]
do
	echo 'SAP Username is empty - try again'
	read -rp 'SAP Username: ' uservar
done 

uservar=$(echo "$uservar" | tr '[:upper:]' '[:lower:]')

if [ "$uservar" == 'sap*' ]
then 
	pause 'Note: Using sap* as the connector user may create additional alerts. Press ENTER to continue.'
fi

read -rsp 'SAP Password: ' passvar
while [ -z "$passvar" ]
do
	echo 'SAP Password empty - try again'
	read -rsp 'SAP Password: ' passvar
done 
echo ''
read -p 'Log Analytics Workspace ID : ' logwsid
while [ -z $logwsid ]
do
	echo 'Log Analytics workspace ID is empty - try again'
	read -p 'Log Analytics Workspace ID : ' logwsid
done 

read -sp 'Log Analytics Public Key: ' logpubkey
while [ -z $logpubkey ]
do
	echo 'Log Analytics Public Key is empty - try again'
	read -sp 'Log Analytics Public Key: ' logpubkey
done 

sed  -i 's/<SET_YOUR_AZURE_KEYVAULT>/'"$kv"'/1' $sysfileloc$sysconf
sed  -i 's/<SET_YOUR_APPLICATION_SERVER_HOST>/'"$hostvar"'/1' $sysfileloc$sysconf
sed  -i 's/<SET_YOUR_SYS_NUMBER>/'"$sysnrvar"'/1' $sysfileloc$sysconf
sed  -i 's/<SET_YOUR_CLIENT>/'"$clientvar"'/1' $sysfileloc$sysconf
sed  -i 's/<SET_YOUR_SYSTEM_ID>/'"$sysid"'/1' $sysfileloc$sysconf
sed  -i 's/<SET_YOUR_PREFIX>/'"$sysid"'/1' $sysfileloc$sysconf

az keyvault secret set  --name $sysid-ABAPPASS   --value "$passvar"   --description SECRET_ABAP_PASS --vault-name $kv >/dev/null
if [ ! $? -eq 0 ];
then 
	echo 'Make sure the key vault has a read/write policy configured for the VM managed identity.'
	exit 1
fi
az keyvault secret set  --name $sysid-ABAPUSER   --value "$uservar"   --description SECRET_ABAP_USER --vault-name $kv >/dev/null
az keyvault secret set  --name $sysid-LOGWSID   --value "$logwsid"   --description SECRET_LOGWSID --vault-name $kv >/dev/null
az keyvault secret set  --name $sysid-LOGWSPUBLICKEY   --value "$logpubkey"   --description SECRET_LOGWSPUBKEY --vault-name $kv >/dev/null

echo '
System information and credentials Has been Updated 
'

sdkfileloc=$(sudo find $(pwd) -name "nwrfc*.zip" -type f | head -1)

if [ -z $sdkfileloc ]
then 
	echo '
Enter the full file location path of your downloaded SAP NetWeaver SDK zip. To download the SDK use the following link: https://launchpad.support.sap.com/#/softwarecenter/template/products/%20_APP=00200682500000001943&_EVENT=DISPHIER&HEADER=Y&FUNCTIONBAR=N&EVENT=TREE&NE=NAVIGATE&ENR=01200314690100002214&V=MAINT&TA=ACTUAL&PAGE=SEARCH/SAP%20NW%20RFC%20SDK


Select SAP NW RFC SDK 7.50 -> Linux on X86_64 64BIT -> Download the latest version

Example: /home/user/nwrfc750P_x-70002752.zip'

	read -p 'SDK file location: ' sdkfileloc 
	
	while [  ! -f "$sdkfileloc" ];
	do
		echo "
	----file $sdkfileloc does not exist----"
		echo '
Enter the full file location path of your downloaded SAP NetWeaver SDK zip. To download the SDK, use the following link: https://launchpad.support.sap.com/#/softwarecenter/template/products/%20_APP=00200682500000001943&_EVENT=DISPHIER&HEADER=Y&FUNCTIONBAR=N&EVENT=TREE&NE=NAVIGATE&ENR=01200314690100002214&V=MAINT&TA=ACTUAL&PAGE=SEARCH/SAP%20NW%20RFC%20SDK

Select SAP NW RFC SDK 7.50 -> Linux on X86_64 64BIT -> Download the latest version

Example: /home/user/nwrfc750P_x-70002752.zip'

		read -p 'SDK file location: ' sdkfileloc 
	done
fi

unzip > /dev/null 2>&1
ifunzip=$?


if [ $ifunzip -eq 0 ]
then
	unzip -Z1 $sdkfileloc |  grep nwrfcsdk/demo/sso2sample.c > /dev/null 2>&1
	sdkok=$?
	sdknum=$(unzip -Z1 $sdkfileloc |  wc -l)
else 
	if [ $(du "$sdkfileloc" | awk '{print $1+0}') -ge 13000 ] 
	then 
		sdkok=0 
		sdknum=35
	else 
		sdkok=1
	fi
fi

while [ $? -eq 1 ] || [ $sdkok -eq 1 ] || [ ! $sdknum -ge 20 ] ;
do
	echo 'Invalid NetWeaver SDK, possibly an incorrect or corrupt file. Download the SDK and try again.'
	read -p 'SDK file location: ' sdkfileloc
	if [ $ifunzip -eq 0 ]
	then
		unzip -Z1 $sdkfileloc |  grep nwrfcsdk/demo/sso2sample.c > /dev/null
		sdkok=$?
		sdknum=$(unzip -Z1 $sdkfileloc |  wc -l)
	else 
		if [ $(du "$sdkfileloc" | awk '{print $1+0}') -ge 13000 ] 
		then 
			sdkok=0 
			sdknum=34 
		else 
			sdkok=1
		fi
	fi
done

sudo docker cp $sdkfileloc $containername:/sapcon-app/inst/ >/dev/null
if [ $? -eq 0 ];
then 
	echo 'SDK archive was successfully updated'
else  
	echo 'Azure Sentinel data connector upgrade failed. The NetWeaver SDK could not be added to the image'
	exit 1
fi


sudo docker start $containername >/dev/null
if [ $? -eq 0 ];
then
	echo '
Azure Sentinel SAP connector was started - quick reference for future steps:
View logs: docker logs '"$containername"'
View logs continuously: docker logs -f '"$containername"'
Stop the connector: docker stop '"$containername"'
Start the connector: docker start '"$containername"'
The process has been successfully completed, thank you!'
else
	echo 'Azure Sentinel Connector upgrade failed – the NetWeaver SDK could not be added to the image'
	exit 1
fi
# Docker Configurations
newgrp docker 