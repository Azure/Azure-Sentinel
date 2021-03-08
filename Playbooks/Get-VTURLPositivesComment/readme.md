[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-VTURLPositivesComment%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-VTURLPositivesComment%2Fazuredeploy.json)

# Get-VTURLPositivesComment
author: Dennis Pike

## Overview
This Playbook queries the VirusTotal API for all the URL entities and gets the total number of positives and adds that as a comment.

## Required Paramaters
- Region<br />
- Playbook Name<br />
- User Name - this is used to pre-populate the username used in the various Azure connections <br />

VirusTotal API Key is required.  You can get one here:
https://www.virustotal.com/gui/join-us<br />

- VirusTotal API Key<br />


### Necessary configuration steps

Once this Playbooks template is deployed, you will need to go into the Logic App, edit it and click on each of the steps that require an authenticated connection to your tenant and complete the connection process.  These steps will have and exclamation point showing that the connection needs to be completed.  Make sure to also open the "For each" step and the "Condition" step within it which also contains steps that require authenticated connections.

