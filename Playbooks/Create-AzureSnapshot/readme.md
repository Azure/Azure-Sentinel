# Create-Snapshot

This playbook will create a snapshot from an Azure VM.

The Logic App uses a Managed System Identity to authenticate and authorize against management.azure.com to create the Snapshot. Be sure to turn on the System Assigned Identity in the Logic App.

The playbook queries LogAnalytics and uses the ResourceID to identify the VM.
The query should map the VM name to the HostCustomEntity in order to identify the right machine to create a snapshot for.

## Quick Deployment

**Deploy with alert trigger**

After deployment, you can run this playbook manually on an alert or attach it to an **analytics rule** so it will rune when an alert is created.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-AzureSnapshot2FCreate-Snapshot.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]("https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FCreate-AzureSnapshot%2FCreate-Snapshot.json)


## Prerequisites

TBD
