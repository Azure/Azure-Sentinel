[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-MDEProcessActivityWithin30Mins%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-MDEProcessActivityWithin30Mins%2Fazuredeploy.json)

# Get-MDEProcessActivityWithin30Mins
author: Dennis Pike

## Overview
This Playbook queries Microsoft Defender for Endpoint telemetry data via the Microsoft 365 Defender Advanced Hunting API for all Process Events that occur within 30 minutes of the incident and adds a comment to the incident specifying the number of Process Events and KQL query that will list all of the events.

## Required Paramaters
- Region<br />
- Playbook Name<br />
- User Name - this is used to pre-populate the username used in the various Azure connections <br />

An Azure AD App registration with required API permissions and secret will needed to provide the following parameters
https://docs.microsoft.com/microsoft-365/security/mtp/api-advanced-hunting?view=o365-worldwide<br />

- Tenant ID<br />
- Client ID<br />
- Secret<br />

The Process Events are stored in a Log Analytics Workspace (preferable the one you have Sentinel enabled on) so you will need the Workspace ID and Workspace Key which can be found under Sentinel > Settings > Workspace Settings > Agents Management

- Workspace ID<br />
- Workspace Key<br />

### Necessary configuration steps

Once this Playbooks template is deployed, you will need to go into the Logic App, edit it and click on each of the steps that require an authenticated connection to your tenant and complete the connection process.  These steps will have and exclamation point showing that the connection needs to be completed.  Make sure to also open the "For each" step and the "Condition 2" step within it which also contains steps that require authenticated connections.