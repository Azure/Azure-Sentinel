# Get-VirusTotalFileInfo
author: Nicholas DiCola

This playbook will take each File Hash entity and query VirusTotal for file report (https://developers.virustotal.com/v3.0/reference#file-info).  You will need to register to thier community for an API key.  If the file last analysis has any suspious or malicous hits a comment will be added to the incident.

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-VirusTotalFileInfo%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-VirusTotalFileInfo%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>
