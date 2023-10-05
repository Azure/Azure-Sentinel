# Dismiss-Upstream-Events
author: Bridewell Consulting - Robert Kitching

This playbook will close/dismiss upstream events in MDATP, MCAS and Azure Security Center when closed in Sentinel. The playbook will run on a preselected recurrence schedule.

*Inspired by [https://github.com/bridewellconsulting/Azure-Sentinel/tree/master/Playbooks/Close-Incident-ASCAlert] (https://github.com/bridewellconsulting/Azure-Sentinel/tree/master/Playbooks/Close-Incident-ASCAlert)*

### Notes

This playbook will account for API pagination. Default page size is set to 50, please alter as appropriate.

The default interval and frequency is set to 6 hours.


### Additional Post Install Notes:

The Logic App uses a Managed System Identity to authenticate and authorize against management.azure.com to retrieve the data from the API. Be sure to turn on the System Assigned Identity in the Logic App.

For MCAS you will need to generate an access token. 

Assign RBAC 'Log Analytic Reader' and 'Security Admin' to the Logic App at the required level.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FDismiss-Upstream-Events%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FDismiss-Upstream-Events%2Fazuredeploy.json)
