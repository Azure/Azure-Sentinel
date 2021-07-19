# Close-Incident-ASCAlert
author: Nathan Swift

This playbook will close the Sentinel incident and will also dismiss the corresponding Azure Security Center alert

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FClose-Incident-ASCAlert%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FClose-Incident-ASCAlert%2Fazuredeploy.json)


**Additional Post Install Notes:**

The Logic App uses a Managed System Identity to authenticate and authorize against management.azure.com to dismiss the ASC Alert. Be sure to turn on the System Assigned Identity in the Logic App. 

Assign RBAC 'Security Admin' role to the Logic App at the Subscription level.