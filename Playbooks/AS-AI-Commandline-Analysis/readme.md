# AI Commandline Analysis with GPT-3
Author: Curtis Middlehurst

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-AI-Commandline-Analysis%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-AI-Commandline-Analysis%2Fazuredeploy.json)

This playbook is intended to be run from a Microsoft Sentinel incident that has a Commandline entity. It will send a prompt to GPT-3 (text-davinci-003 model) and return an explanation of the commandline to the comments of the incident.

#
### Requirements

1. An OpenAI API Key to authorise the GPT-3 connection.

# 
### Setup

Before you begin, you will need to have an API key from https://openai.com/api/. 

**USAGE OF THE OPENAI API IS NOT FREE**, please ensure you are aware of this before usage and select the appropriate plan for your organisation according to https://openai.com/api/pricing/.

#
### Deployment

To configure and deploy this playbook:

Open your browser and ensure you are logged into your Microsoft Sentinel workspace.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-AI-Commandline-Analysis%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAS-AI-Commandline-Analysis%2Fazuredeploy.json)

Click the “**Deploy to Azure**” button at the bottom and it will bring you to the custom deployment template.

1. Select a name for the Playbook.

#
### Setting up the OpenAI Connector

Before you begin, you will need to have an API key from https://openai.com/api/. 

Go to *yourlogicappname* -> API Connections -> *openaiip-yourlogicappname* -> Edit API Connection
Set the 'API Key' to 'Bearer *yourapikey*'.
![OpenAiAPIKey](Images/openaiapikey.png)

#
### Assigning the Responder role to the playbook

The playbook uses a managed identity, this identity needs the Microsoft Sentinel Responder role in any Sentinel instances in order to add comments.

1. Select the Playbook resource.
2. In the left menu, click Identity.
3. Under Permissions, click Azure role assignments.
4. Click Add role assignment (Preview).
5. Use the drop-down lists to select the resource group that your *Sentinel Workspace* is in. If multiple workspaces are used in different resource groups consider selecting subscription as a scope instead.
6. In the Role drop-down list, select the role 'Microsoft Sentinel Responder'.
7. Click Save to assign the role.
#
### Usage
This playbook can be run manually or as part of an automation rule. This has been tested against incidents with a commandline entity, without a commandline entity and with multiple commandline entities and has handled each appropriately.

Once the playbook runs on an incident, the GPT-3 Analysis of any commandlines appear in the comments.
![CommandlineAnalysisExample](Images/cmdanalysis.png)
#
