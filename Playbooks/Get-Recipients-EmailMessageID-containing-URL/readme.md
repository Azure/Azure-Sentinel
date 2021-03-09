[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-Recipients-EmailMessageID-containing-URL%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-Recipients-EmailMessageID-containing-URL%2Fazuredeploy.json)

# Get-Recipients-EmailMessageID-containing-URL
author: Dennis Pike

## Overview
This Playbook queries Microsoft Defender for o365 telemetry data via the Microsoft 365 Defender Advanced Hunting API for all emails that contain URL incident entities and adds a comment to the incident listing the URLs with Recipients and Email Message IDs.

## Required Paramaters
- Region<br />
- Playbook Name<br />
- User Name - this is used to pre-populate the username used in the various Azure connections <br />

An Azure AD App registration with required API permissions and secret will needed to provide the following parameters
https://docs.microsoft.com/microsoft-365/security/mtp/api-advanced-hunting?view=o365-worldwide<br />

- Tenant ID<br />
- Client ID<br />
- Secret<br />

### Necessary configuration steps

Once this Playbooks template is deployed, you will need to go into the Logic App, edit it and click on each of the steps that require an authenticated connection to your tenant and complete the connection process.  These steps will have an exclamation point showing that the connection needs to be completed.  Make sure to also open the "For each" step which also contains a step that requires an authenticated connection.