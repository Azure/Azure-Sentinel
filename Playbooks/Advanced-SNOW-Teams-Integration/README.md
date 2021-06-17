# Advanced - ServiceNow & Teams Integration
Author: Jing Nghik

![Alt Text](./Media/animated.gif)

This arm template will deploy multiple logic app playbooks and api connectors. 
- (Main playbook) \<deploymentName>-\<playbookName>
- (playbook function) - \<deploymentName>-GetPlaybooksbyTag
This playbooks purpose is to locate any playbooks that have been tagged with playbook to populate the Investigation Response list dynamically.
- (Check IP - Example playbook) - \<deploymentName>-CheckIPonVirusTotal - Simple playbook to checkIPonVirusTotal. This playbook is an example that will be available in Azure Sentinel and the main playbook.
- All the API connectors are reused across the same playbook to prevent duplicate API connectors created. 

There are a number of pre-configuration steps required before deploying the Logic App.

## Requirements
In order to fully utilize this playbook. You will need the following:
- ServiceNow instance URL, Username, and password
You can create a dev environment to test with for free at https://developer.servicenow.com/dev.do
- access/authorization to enable api connectors for Azure resource manager, teams, and azure sentinel.
- Teams Group ID, Alert Channel ID, Investigation Response Channel ID 
The group ID and Channel ID can be obtained by going to Teams and getting the link which has the values you need for the parameters. (Will need to URL decode it if there are special characters) [URL Decoder Link](https://www.urldecoder.org/)
![Alt Text](./Media/teams.png)
-- Investigation Channel ID can also use the same ID as alert channel if desired. 

## Workflow
1. Based on the rules, Azure Sentinel triggers an incident or alert. 
2. This runs a linked playbook that first will check if an existing serviceNow ticket already exists (to prevent duplicate tickets)
3. The ticket is opened is serviceNow and a Teams message is sent to the Alert channel with alert/incident details.
4. A corresponding investigation response message is sent with a list of available playbooks that can be run from teams. 
5. Based on the input provided, the selected playbooks are ran ad-hoc and playbook results/response is attached to the same alert channel message thread. 

## Setup Steps
1. Click Deploy to Azure and fill in parameters
2. Search for API connectors and find the deployment prefix and fix any connectors by authorizing the connection.
3. Populate the Teams Group and Channel IDs to ensure it messages are generated in the right channel.
3. Manually trigger an azure sentinel alert to test. 

Thanks the following people for contributing to my efforts in building this playbook!
- Twitter@thijslecomte - For showing me how to make my first template!
- Jan Ignacio, Joey Cruz, Sreedhar Ande, Nicholas Dicola, Rod Trent, Nathan Swift

## Deploy the ARM template
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAdvanced-SNOW-Teams-Integration%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Playbooks/Advanced-SNOW-Teams-Integration/azuredeploy.json)
