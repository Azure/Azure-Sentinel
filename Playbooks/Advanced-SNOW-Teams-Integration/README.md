# Advanced - ServiceNow & Teams Integration
**Author:** Jing Nghik

![Alt Text](./Media/animated.gif)

This arm template will deploy multiple logic app playbooks and api connectors. 
- **(Main playbook)** \<playbookName>-workflow-incident
- **(playbook function)** - \<playbookName>-function-getListOfTaggedPlaybooks
This playbooks purpose is to locate any playbooks that have been tagged with playbook to populate the Investigation Response list dynamically.
- **(Check IP - Example playbook)** - \<playbookName>-checkIPOnVirusTotal - Simple playbook to check IP on VirusTotal. This playbook is an example that will be available in Azure Sentinel and the main playbook.
- All the API connectors are reused across the same playbook to prevent duplicate API connectors created. 

## Updates
- Migrated playbook to support incidents instead of alerts
- fixed some JSON parsing problems with adaptive cards by adding an compose action to render the card.

Video Walkthrough
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/RgspwmcwjxQ/0.jpg)](https://www.youtube.com/watch?v=RgspwmcwjxQ)

## Requirements
In order to fully utilize this playbook. There are a number of pre-configuration steps required before deploying the Logic App.

**You will need the following:**
- ServiceNow instance URL, Username, and password
You can create a dev environment to test with for free at https://developer.servicenow.com/dev.do
- access/authorization to enable api connectors for Azure resource manager, teams, and azure sentinel.
- Teams Group ID, Alert Channel ID, Investigation Response Channel ID 
The group ID and Channel ID can be obtained by going to Teams and getting the link which has the values you need for the parameters. (Will need to URL decode it if there are special characters). [URL Decoder Link](https://www.urldecoder.org/)
![Alt Text](./Media/teams.png)

- Investigation Channel ID can also use the same ID as alert channel if desired. 

## Workflow
1. Based on the rules, Azure Sentinel triggers an incident or alert. 
2. This runs a linked playbook that first will check to determine if an existing serviceNow ticket already exists with the same incident ID (to prevent duplicate tickets)
3. The ticket is opened in serviceNow and a Teams message is created in the Alerts channel with alert/incident details.
4. A corresponding investigation response message is sent with a list of available playbooks that can be run from teams. 
5. Based on selected playbooks submitted, the playbooks are ran ad-hoc by routing the alert body to the selected playbook.
6. If the executed playbook returns a response, that message is updated in the related serviceNow ticket, commented in the Azure Sentinel Incident, and also added added as a reply to the Initial Teams Alert message.

## Setup Steps
1. Click Deploy to Azure and fill in parameters
2. Populate the Teams Group and Channel IDs to ensure it messages are generated in the right channel.
3. Search for API connectors and find the deployment prefix and fix any connectors by authorizing the connection.
![Alt Text](./Media/apiconnectors.png)
4. Manually trigger an azure sentinel alert to test. 

## Deploy the ARM template
<a href="https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FAdvanced-SNOW-Teams-Integration%2Fazuredeploy.json" target="_blank"><img src="https://aka.ms/deploytoazurebutton"/></a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Playbooks/Advanced-SNOW-Teams-Integration/azuredeploy.json" target="_blank"><img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/></a>

## Thanks!
**Thank you to the following people for contributing to my efforts in building this playbook!**
- Twitter [@thijslecomte](https://twitter.com/thijslecomte) - For showing me how to make my first template!
- **Jan Ignacio, Joey Cruz, Sreedhar Ande, Nicholas Dicola, Rod Trent, Nathan Swift** for pushing me to contribute to this repo, testing, and feedback.

## Todo list 
- Have the playbook support buth alerts and incidents. (Only works for alerts)
- A way to support other messaging services and ticketing platforms
- selectable card templates
- Way to not create a new teams thread if one already exists. 
- support pager duty and teams on-call.
