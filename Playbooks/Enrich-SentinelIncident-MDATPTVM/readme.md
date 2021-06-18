# Enrich-SentinelIncident-MDATPTVM
author: Yaniv Shasha

This playbook will enrich the Client machine that is part of sentinel incident with thread vulnerabilities data (TVM) with CVE that their score is grater then 7.5.
Also it automatically add this information to the incident as comments and change the incident severity to High."


Prerequisite:

<li>Oauth2 to authenticate:
<ul>
<li><a href="https://docs.microsoft.com/en-us/windows/security/threat-protection/microsoft-defender-atp/apis-intro " target="_blank" rel="noopener">This logic app use Oauth2 to authenticate against MDATP API</a></li>
</ul>
</li>



<li>Create AAD app:
<ul>
<li><a href="https://docs.microsoft.com/en-us/windows/security/threat-protection/microsoft-defender-atp/get-all-vulnerabilities#permissions" target="_blank" rel="noopener">create AAD app and give the Permissions based on this article</a></li>
</ul>
</li>




<href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FEnrich-SentinelIncident-MDATPTVM%2Fazuredeploy.json" target="_blank">
   <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FEnrich-SentinelIncident-MDATPTVM%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>