# Run-Notebook-After-Incident-Creation
author: Zhipeng Zhao

This playbook will trigger a Microsoft Sentinel notebook to process newly created incident.  It will pass incident ID and entities if any to the notebook.  


## Prerequisites

Before deploying the the playbook you will need 
- set up Sentinel notebook automation system with a Synapse workspace (more info coming), 
- upload incident related notebooks and create pipelines for the notebooks (more info coming).  
- gather Synapse workspace name and Synapse pipeline name for template deployment.

## Quick Deployment
[Learn more about playbook deployment](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/ReadMe.md)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRun-Notebook-After-Incident-Creation%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FRun-Notebook-After-Incident-Creation%2Fazuredeploy.json)

## Post-Deployment
[Learn more about automation rules](https://docs.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules#creating-and-managing-automation-rules)

After deployment, attach this playbook to an **automation rule** so it runs when the incident is created.

Then, the Logic App's system generated identity needs to be added to the targeted Synapse workspace as a Synapse Administrator through Synapse Studio.
