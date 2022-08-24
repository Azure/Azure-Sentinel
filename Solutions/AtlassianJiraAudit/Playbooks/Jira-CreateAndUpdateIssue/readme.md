# Jira-CreateAndUpdateIssue
author: Benjamin Kovacevic

This playbook will create or update incident in Jira. When incident is created, playbook will run and create issue in Jira. When incident is updated, playbook will run and add update to comment section.

# Prerequisites

We will need following data to make Jira connector:<br>
1. Jira instance (ex. xyz.atlassian.net)<br>
2. Jira API (create API token on https://id.atlassian.com/manage-profile/security/api-tokens)<br>
3. User email<br>
![Jira connector requirements](./images/jira-connector-requirementsDark.png)<br>

# Quick Deployment
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAtlassianJiraAudit%2FPlaybooks%2FJira-CreateAndUpdateIssue%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAtlassianJiraAudit%2FPlaybooks%2FJira-CreateAndUpdateIssue%2Fazuredeploy.json)
<br><br>

# Post-deployment
1. Authorize Jira connector and choose:
- Jira Project (where you want to sync Microsoft Sentinel incidents to) and
- Issue Type Id (Microsoft Sentinel incident issue type in Jira - Task, Story, Bug,...).<br>
2. Assign Microsoft Sentinel Responder role to playbook's managed identity. To do so, choose Identity blade under Settings of the Logic App.
3. Add playbook as an action to the automation rule, ex.:
- Trigger = When incident is updated;  
- Condition = Staus > Changed To > Closed;.<br>
**Automation rule example**<br>
![Automation Rule Example](./images/AutomationRuleExampleDark.jpg)

# Screenshots

**Playbook** <br>
![playbook screenshot](./images/JiraPlaybookDark.jpg)<br>
![playbook screenshot](./images/JiraPlaybookLight.jpg)<br><br>

**Jira New Issue** <br>
![jira screenshot new](./images/JiraNewIssue.jpg)<br><br>

**Jira Update Issue** <br>
![jira screenshot update](./images/JiraUpdateIssue.jpg)<br>