#!/bin/bash

# if [ "$EUID" -ne 0 ]
#   then echo "Please run as root"
#   exit
# fi

echo '

************************************************************

THIS EXAMPLE INSTALLATION SCRIPT WILL LEVERAGE ROOT ACCESS TO :

1. INSTALL DOCKER & UNZIP

2. ADD THE CURRENT USER TO THE DOCKER GROUP

3. EXECUTE THE CONNECTOR AS DOCKER CONTAINER ON THE HOST

*************************************************************

Microsoft Azure Sentinel SAP Continuous Threat Monitoring.
SAP ABAP Logs Connector - Limited Private Preview

Copyright (c) Microsoft Corporation. This preview software is Microsoft Confidential, and is subject to your Non-Disclosure Agreement with Microsoft. 
You may use this preview software internally and only in accordance with the Azure preview terms, located at https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/  

Microsoft reserves all other rights
****'

function pause(){
   read -p "$*"
}

echo '
-----Sapcon on Azure – ABAP only KickStart----

In order to complete the installation process:
SAP Continuous Threat Monitoring container registry password is needed. 
The access and password must be granted explicitly to you by Microsoft, is personal and may not be shared. 

SAP version -> The Azure Sentinel SAP Logs connector requires a SAP version of 7.4 or higher.

SAP system details -> Make a note of your SAP system IP address, system number, system ID, and client.

SAP change requests -> Import any required change requests for your logs from the CR folder of this repository - https://github.com/Azure/AzureSentinel4SAP/tree/main/CR.
The following table lists the SAP Log change requests that you must configure in order to support ingesting specific SAP logs into Azure Sentinel.
For a typical installation on SAP Basis 7.5+ install S4HK900121
For a typical installation on SAP Basis 7.4 install S4HK900119
For the role creation (any version) install S4HK900086
Tip: To create the role with all required authorizations, deploy the SAP change request S4HK9000862 on your SAP system. This change request creates the zsentinel_connector role, and assigns the role to the ABAP connecting to Azure Sentinel.

SAP notes required for version below SAP Basis 7.5 SP13:
SAP Note 2641084 (Standardized read access for the Security Audit log data)
SAP Note 2173545 (CD: CHANGEDOCUMENT_READ_ALL)
SAP Note 2502336 (CD: RSSCD100 - read only from archive, not from database)
Note: The required SAP log change requests expose custom RFC FMs that are required for the connector, and do not change any standard or custom objects.

For more information see the SAP documentation.
'

pause '[Press enter to agree and proceed as we will guide you through the installation process or control +  c to cancel the process]'


#Globals
dockerimage=mcr.microsoft.com/azure-sentinel/solutions/sapcon
containername=sapcon
sysconf=systemconfig.ini
tagver=":latest"
logwsid=LOGWSID
logwspubkey=LOGWSPUBLICKEY
abapuser=ABAPUSER
abappass=ABAPPASS

os=$(cat /etc/os-release | awk 'BEGIN { FS="=" } $1=="ID" {print $2}')
ver_id=$(cat /etc/os-release | awk 'BEGIN { FS="=" } $1=="VERSION_ID" {print $2}' | awk '{print substr($0, 2, length($0) - 2) }')
id_like=$(cat /etc/os-release | awk 'BEGIN { FS="=" } $1=="ID_LIKE" {print $2}')

echo 'Starting OS update, Notice that this action can take a few minutes '

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
	echo VM version is not sufficient, Please create one of the following vm os image : ubuntu ver >=18.04 / sles ver >= 15 / rhel ver >=7.7
	exit 1
fi


# sudo groupadd docker
sudo usermod -aG docker $USER
az login --identity --allow-no-subscriptions >/dev/null 2>&1
if [ ! $? -eq 0 ]
then 
	echo 'Looks like the vm is not set with managed identity or the az client was not installed correctly, 
Please set and grant relevant KV permissions and make sure az cli is installed.'
	exit 1
fi  

echo '
VM is ready to deploy Azure Sentinel SAP connector, all OS dependencies are met
'

echo 'Starting Docker image Pull'
sudo docker pull $dockerimage
if [ $? -eq 1 ];
then 
	echo 'There is an error downloading the Sentinel SAP connector from the online repository, please contact Microsoft for support'
	exit 1
fi
pause 'Latest Sentinel Connector has been downloaded - Press <Enter> key to continue
'
echo 'Enter the following information regarding Your SAP instance
'
read -p 'Hostname: ' hostvar
read -p 'System Number: ' sysnrvar
read -p 'SID : ' sysid
while [ ${#sysid} -ne 3 ] 
do
	echo 'SID is invalid - Try again'
	read -p 'SID: ' sysid
done 

read -p 'Client: ' clientvar
while [ ${#clientvar} -ne 3 ]
do
	echo 'Client is invalid - Try again'
	read -p 'Client: ' clientvar
done 

echo '
Testing network access to SAP instance'
timeout 2 nc -z $hostvar 33$sysnrvar >/dev/null
portcheck1=$?

if [ ! $portcheck1 -eq 0 ]
then
	echo "Port 33$sysnrvar is not accessible, Please allow access and start again"
	exit 1
fi

timeout 2 nc -z $hostvar 32$sysnrvar
portcheck2=$?
if [ ! $portcheck2 -eq 0 ]
then
	echo "Port 32$sysnrvar is not accessible, Please allow access and start again"
	exit 1
fi
echo 'SAP system is reachable
'

sysfileloc=$(pwd)/$containername/$sysid/
mkdir -p $sysfileloc
if [ ! $? -eq 0 ];
then 
	echo 'There is an error creating The local folder '
	exit 1
fi

containername="$containername-$sysid"

sudo docker create -v $sysfileloc:/sapcon-app/sapcon/config/system --name $containername $dockerimage$tagver >/dev/null
if [ $? -eq 1 ];
then 
	echo '
Sentinel SAP connector is already installed, the previous connector will be removed and replaced by the new version'
	pause 'Press any key to update'
	sudo docker stop $containername >/dev/null
	sudo docker container rm $containername >/dev/null
	sudo docker create -v $sysfileloc:/sapcon-app/sapcon/config/system --name $containername $dockerimage >/dev/null
	echo 'Sentinel SAP connector was updated for instance '"$sysid"
	pause 'Press any key to continue'
fi


sudo docker cp $containername:/sapcon-app/template/systemconfig-kickstart.ini "$sysfileloc"systemconfig.ini
if [ ! $? -eq 0 ];
then 
	echo 'There is an error accessing The local folder '
	exit 1
fi
# sudo docker cp $containername:/sapcon-app/template/loggingconfig_PRD.yaml "$sysfileloc"loggingconfig.yaml
# if [ ! $? -eq 0 ];
# then 
# 	echo 'There is an error accessing The local folder '
# 	exit 1
# fi

echo 'Enter the you KV name Following with Your SAP and Sentinel Credentials
Make sure that this VM has identity with the relevant auth for KV'

read -p 'KeyVault Name: ' kv
while [ -z $kv ]
do
	echo 'KeyVault is empty - Try again'
	read -p 'KeyVault: ' kv
done 

read -rp 'SAP Username: ' uservar
while [ -z "$uservar" ]
do
	echo 'SAP Username is empty - Try again'
	read -rp 'SAP Username: ' uservar
done 

uservar=$(echo "$uservar" | tr '[:upper:]' '[:lower:]')

if [ "$uservar" == 'sap*' ]
then 
	pause 'Notice that using sap* as the connector user can create additional alerts - Press enter to continue'
fi

read -rsp 'SAP Password: ' passvar
while [ -z "$passvar" ]
do
	echo 'SAP Password empty - Try again'
	read -rsp 'SAP Password: ' passvar
done 
echo ''
read -p 'Log Analytics Workspace ID : ' logwsid
while [ -z $logwsid ]
do
	echo 'Log Analytics Workspace ID is empty - Try again'
	read -p 'Log Analytics Workspace ID : ' logwsid
done 

read -sp 'Log Analytics Public Key: ' logpubkey
while [ -z $logpubkey ]
do
	echo 'Log Analytics Public Key is empty - Try again'
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
	echo 'Please ensure the keyvault has a configured policy for read and write for the VM managed identity'
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
Please enter the full file location path of your downloaded SAP NetWeaver SDK zip that has been downloaded, to download follow the link below

https://launchpad.support.sap.com/#/softwarecenter/template/products/%20_APP=00200682500000001943&_EVENT=DISPHIER&HEADER=Y&FUNCTIONBAR=N&EVENT=TREE&NE=NAVIGATE&ENR=01200314690100002214&V=MAINT&TA=ACTUAL&PAGE=SEARCH/SAP%20NW%20RFC%20SDK

Select SAP NW RFC SDK 7.50 -> Select Linux on X86_64 64BIT -> Download the latest version

Example: /home/user/nwrfc750P_7-70002752.zip'

	read -p 'SDK file location: ' sdkfileloc 
	
	while [  ! -f "$sdkfileloc" ];
	do
		echo "
	----file $sdkfileloc does not exist----"
		echo '
Please enter the full file location path of your downloaded SAP NetWeaver SDK zip that has been downloaded, to download follow the link below

https://launchpad.support.sap.com/#/softwarecenter/template/products/%20_APP=00200682500000001943&_EVENT=DISPHIER&HEADER=Y&FUNCTIONBAR=N&EVENT=TREE&NE=NAVIGATE&ENR=01200314690100002214&V=MAINT&TA=ACTUAL&PAGE=SEARCH/SAP%20NW%20RFC%20SDK

Select SAP NW RFC SDK 7.50 -> Select Linux on X86_64 64BIT -> Download the latest version

Example: /home/user/nwrfc750P_7-70002752.zip
'
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
	if [ $(du "$sdkfileloc" | awk '{print $1+0}') -ge 16000 ] 
	then 
		sdkok=0 
		sdknum=34 
	else 
		sdkok=1
	fi
fi

while [ $? -eq 1 ] || [ $sdkok -eq 1 ] || [ ! $sdknum -ge 34 ] ;
do
	echo 'The NetWeaver SDK provided/found is invalid, likely an incorrect version or corrupt file, Please download the file and try again'
	read -p 'SDK file location: ' sdkfileloc
	if [ $ifunzip -eq 0 ]
	then
		unzip -Z1 $sdkfileloc |  grep nwrfcsdk/demo/sso2sample.c > /dev/null
		sdkok=$?
		sdknum=$(unzip -Z1 $sdkfileloc |  wc -l)
	else 
		if [ $(du "$sdkfileloc" | awk '{print $1+0}') -ge 16000 ] 
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
	echo 'Sentinel Connector upgrade failed – the NetWeaver SDK could not be added to the image. Please contact Microsoft for support'
	exit 1
fi


sudo docker start $containername >/dev/null
if [ $? -eq 0 ];
then
	echo '
Sentinel SAP connector was started- quick reference for future steps:
View logs: docker logs '"$containername"'
View logs continuously docker logs -f '"$containername"'
Stop the connector: docker stop '"$containername"'
Start the connector: docker start '"$containername"'
The process has been successfully completed, thank you !'
else
	echo 'Sentinel Connector upgrade failed – the NetWeaver SDK could not be added to the image. Please contact Microsoft for support'
	exit 1
fi
# Docker Configurations
sudo chown -R  $USER:$USER ~/.docker >/dev/null
newgrp docker 