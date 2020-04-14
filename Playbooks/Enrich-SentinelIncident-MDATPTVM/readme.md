# Enrich-SentinelIncident-MDATPTVM
author: Yaniv Shasha

This playbook will enrich the Client machine that is part of sentinel incident with thread vulnerabilities data (TVM) with CVE that their score is grater then 7.5.
Also it automatically add this information to the incident as comments and change the incident severity to High."

This playbook will enrich the Client machine that is part of sentinel incident with thread vulnerabilities data (TVM) with CVE that their score is grater then 7.5.
Also it automatically add this information to the incident as comments and change the incident severity to High.

Prerequisite:

This logic app use Oauth2 to authenticate against MDATP API:
https://docs.microsoft.com/en-us/windows/security/threat-protection/microsoft-defender-atp/apis-intro 

Please follow this documentation to create AAD app and give the Permissions based on this article:

https://docs.microsoft.com/en-us/windows/security/threat-protection/microsoft-defender-atp/get-all-vulnerabilities#permissions

<a href="https://azuredeploy.net/?repository=https://github.com/Yaniv-Shasha/Sentinel/tree/master/Playbooks/Enrich-SentinelIncident-MDATPTVM" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FYaniv-Shasha%2FSentinel%2Fmaster%2FPlaybooks%2FEnrich-SentinelIncident-MDATPTVM%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>