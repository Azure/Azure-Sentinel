#!/bin/zsh
SCRIPT=$(realpath "$0")
SCRIPTPATH=$(dirname "$SCRIPT")
cd "$SCRIPTPATH"

cd ../../
pwsh ./Tools/Create-Azure-Sentinel-Solution/createSolution.ps1

configFile=./Solutions/CohesitySecurity/cohesity.config
send_to_email_for_playbook=`cat ${configFile} |awk -F'=' '/send_to_email_for_playbook/{print $2}'`
cohesity_support_email=`cat ${configFile} |awk -F'=' '/cohesity_support_email/{print $2}'`
apiKey_string=`cat ${configFile} |awk -F'=' '/apiKey_string/{print $2}'`
sed -i.bak "s/send_to_email_for_playbook/$send_to_email_for_playbook/g;s/cohesity_support_email/$cohesity_support_email/g;s/apiKey_string/$apiKey_string/g" ./Solutions/CohesitySecurity/Package/mainTemplate.json
