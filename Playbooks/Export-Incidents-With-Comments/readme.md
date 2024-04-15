# Export-Incidents-With-Comments
author: Bridewell Consulting - Robert Kitching

This playbook will export all incidents and comments and email them in an CSV file. The filter date is linked to the recurrence trigger settings.

### Notes

This playbook will account for API pagination. Default page size is set to 50, please alter as appropriate.

If you wish to alter the output columns etc please alter the 'Append to array variable' action within the main loop.

### Annotated Guide

For an annotated breakdown of this playbook please visit [https://www.bridewellconsulting.com/automating-azure-sentinel-using-playbooks-to-extract-data](https://www.bridewellconsulting.com/automating-azure-sentinel-using-playbooks-to-extract-data).

### Additional Post Install Notes:

The Logic App uses a Managed System Identity to authenticate and authorize against management.azure.com to retrieve the data from the API. Be sure to turn on the System Assigned Identity in the Logic App.

Assign RBAC 'Log Analytic Reader' role to the Logic App at the required level.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FExport-Incidents-With-Comments%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FExport-Incidents-With-Comments%2Fazuredeploy.json)